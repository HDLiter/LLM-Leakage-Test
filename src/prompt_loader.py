"""Utilities for loading, rendering, and validating frozen prompt catalogs."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .masking import extract_json_robust

try:
    import yaml
except ImportError as exc:
    raise ImportError(
        "PyYAML is required. Install with: "
        "conda run -n rag_finance python -m pip install pyyaml"
    ) from exc

if TYPE_CHECKING:
    from .llm_client import LLMClient


@dataclass(slots=True)
class TaskPrompt:
    prompt_id: str
    system_prompt: str
    user_prompt_template: str
    output_schema: dict[str, Any]
    approx_max_output_tokens: int
    task_family: str
    variant: str
    experiments: list[str] = field(default_factory=list)
    slot_semantics: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass(slots=True)
class CFTemplate:
    template_id: str
    system_prompt: str
    user_prompt_template: str
    output_schema: dict[str, Any]
    approx_max_output_tokens: int
    applicable_to: list[str] = field(default_factory=list)
    experiments: list[str] = field(default_factory=list)


_REPO_ROOT = Path(__file__).resolve().parent.parent
_VALIDATOR_MODULES: dict[Path, Any] = {}
_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _load_validator_module(path: Path) -> Any:
    resolved = path.resolve()
    cached = _VALIDATOR_MODULES.get(resolved)
    if cached is not None:
        return cached

    if not resolved.exists():
        raise FileNotFoundError(f"Schema validator not found: {resolved}")

    module_name = f"_prompt_schema_validation_{abs(hash(str(resolved)))}"
    spec = importlib.util.spec_from_file_location(module_name, resolved)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load schema validator module from {resolved}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _VALIDATOR_MODULES[resolved] = module
    return module


class PromptLoader:
    """Load prompt catalogs, render prompts, and validate model outputs."""

    def __init__(self, prompts_dir: str | Path = "config/prompts"):
        self.prompts_dir = self._resolve_prompts_dir(prompts_dir)
        self.task_catalog_path = self.prompts_dir / "task_prompts.yaml"
        self.cf_catalog_path = self.prompts_dir / "counterfactual_templates.yaml"
        self.validator_path = self.prompts_dir / "schema_validation.py"

        self._validator = _load_validator_module(self.validator_path)
        self._task_catalog = self._load_yaml(self.task_catalog_path)
        self._cf_catalog = self._load_yaml(self.cf_catalog_path)

        self._task_prompts = self._build_task_prompts()
        self._cf_templates = self._build_cf_templates()

    def get_task_prompt(self, task_id: str) -> TaskPrompt:
        """Return a task prompt definition."""
        try:
            return copy.deepcopy(self._task_prompts[task_id])
        except KeyError as exc:
            available = ", ".join(self.list_task_ids())
            raise KeyError(
                f"Unknown task prompt id {task_id!r}. Available ids: {available}"
            ) from exc

    def get_counterfactual_template(self, template_id: str) -> CFTemplate:
        """Return a counterfactual template definition."""
        try:
            return copy.deepcopy(self._cf_templates[template_id])
        except KeyError as exc:
            available = ", ".join(self.list_cf_template_ids())
            raise KeyError(
                f"Unknown counterfactual template id {template_id!r}. "
                f"Available ids: {available}"
            ) from exc

    def list_task_ids(self) -> list[str]:
        """List all known task prompt ids."""
        return list(self._task_prompts.keys())

    def list_cf_template_ids(self) -> list[str]:
        """List all known counterfactual template ids."""
        return list(self._cf_templates.keys())

    def render_user_prompt(self, task_id: str, article: str, **kwargs: Any) -> str:
        """Render a task prompt user message."""
        prompt = self.get_task_prompt(task_id)
        return self._render_template(
            prompt.user_prompt_template,
            values={"article": article, **kwargs},
            context=f"task prompt {task_id!r}",
        )

    def render_cf_prompt(self, template_id: str, article: str, **kwargs: Any) -> str:
        """Render a counterfactual template user message."""
        template = self.get_counterfactual_template(template_id)
        return self._render_template(
            template.user_prompt_template,
            values={"article": article, **kwargs},
            context=f"counterfactual template {template_id!r}",
        )

    def validate_output(self, task_id: str, output: dict[str, Any]) -> list[str]:
        """Validate task output against the frozen schema and slot semantics."""
        raw_prompt, schema = self._validator.resolve_task_schema(
            self._task_catalog, task_id
        )
        errors = list(self._validator.validate_schema(schema, output))
        if isinstance(output, dict):
            errors.extend(self._validator.validate_slot_semantics(raw_prompt, output))
        return errors

    def run_task(
        self,
        client: LLMClient,
        task_id: str,
        article: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Render a task prompt, call the client, parse JSON, and validate it."""
        prompt = self.get_task_prompt(task_id)
        user_prompt = self.render_user_prompt(task_id, article, **kwargs)
        response = client.chat(prompt.system_prompt, user_prompt)
        parsed = self._parse_json_object(response.raw_response, context=f"task {task_id!r}")

        errors = self.validate_output(task_id, parsed)
        if errors:
            raise ValueError(
                f"LLM output failed validation for task {task_id!r}: "
                + "; ".join(errors)
            )
        return parsed

    def resolve_slots(self, task_id: str, output: dict[str, Any]) -> dict[str, Any]:
        """Replace generic slot keys with semantic field names for matched prompts."""
        prompt = self.get_task_prompt(task_id)
        mapping = {
            slot_name: spec.get("meaning", slot_name)
            for slot_name, spec in prompt.slot_semantics.items()
        }
        if not mapping:
            return copy.deepcopy(output)

        resolved: dict[str, Any] = {}
        for key, value in output.items():
            target_key = mapping.get(key, key)
            if key == "evidence" and isinstance(value, list):
                resolved[target_key] = [
                    self._resolve_evidence_item(item, mapping) for item in value
                ]
                continue
            resolved[target_key] = copy.deepcopy(value)
        return resolved

    def _resolve_prompts_dir(self, prompts_dir: str | Path) -> Path:
        path = Path(prompts_dir)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        return path.resolve()

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Prompt catalog not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Prompt catalog {path} must load to a mapping")
        return data

    def _build_task_prompts(self) -> dict[str, TaskPrompt]:
        raw_prompts = self._task_catalog.get("prompts")
        if not isinstance(raw_prompts, dict):
            raise ValueError(
                f"{self.task_catalog_path} must define a top-level 'prompts' mapping"
            )

        prompts: dict[str, TaskPrompt] = {}
        for task_id in raw_prompts:
            raw_prompt, schema = self._validator.resolve_task_schema(
                self._task_catalog, task_id
            )
            prompts[task_id] = self._make_task_prompt(task_id, raw_prompt, schema)
        return prompts

    def _build_cf_templates(self) -> dict[str, CFTemplate]:
        raw_templates = self._cf_catalog.get("templates")
        if not isinstance(raw_templates, dict):
            raise ValueError(
                f"{self.cf_catalog_path} must define a top-level 'templates' mapping"
            )

        templates: dict[str, CFTemplate] = {}
        for template_id in raw_templates:
            raw_template, schema = self._validator.resolve_counterfactual_schema(
                self._cf_catalog, template_id
            )
            templates[template_id] = self._make_cf_template(
                template_id, raw_template, schema
            )
        return templates

    def _make_task_prompt(
        self,
        task_id: str,
        raw_prompt: dict[str, Any],
        schema: dict[str, Any],
    ) -> TaskPrompt:
        required = (
            "system_prompt",
            "user_prompt_template",
            "approx_max_output_tokens",
            "task_family",
            "variant",
            "experiments",
        )
        self._require_keys(raw_prompt, required, context=f"task prompt {task_id!r}")

        slot_semantics = raw_prompt.get("slot_semantics", {})
        if not isinstance(slot_semantics, dict):
            raise ValueError(
                f"task prompt {task_id!r} has invalid 'slot_semantics'; expected a mapping"
            )

        return TaskPrompt(
            prompt_id=task_id,
            system_prompt=str(raw_prompt["system_prompt"]),
            user_prompt_template=str(raw_prompt["user_prompt_template"]),
            output_schema=self._require_mapping(
                schema, context=f"output schema for task prompt {task_id!r}"
            ),
            approx_max_output_tokens=int(raw_prompt["approx_max_output_tokens"]),
            task_family=str(raw_prompt["task_family"]),
            variant=str(raw_prompt["variant"]),
            experiments=self._coerce_string_list(
                raw_prompt["experiments"], context=f"task prompt {task_id!r} experiments"
            ),
            slot_semantics=self._require_mapping(
                slot_semantics, context=f"slot semantics for task prompt {task_id!r}"
            ),
        )

    def _make_cf_template(
        self,
        template_id: str,
        raw_template: dict[str, Any],
        schema: dict[str, Any],
    ) -> CFTemplate:
        required = (
            "system_prompt",
            "user_prompt_template",
            "approx_max_output_tokens",
            "applicable_to",
            "experiments",
        )
        self._require_keys(
            raw_template, required, context=f"counterfactual template {template_id!r}"
        )

        return CFTemplate(
            template_id=template_id,
            system_prompt=str(raw_template["system_prompt"]),
            user_prompt_template=str(raw_template["user_prompt_template"]),
            output_schema=self._require_mapping(
                schema,
                context=f"output schema for counterfactual template {template_id!r}",
            ),
            approx_max_output_tokens=int(raw_template["approx_max_output_tokens"]),
            applicable_to=self._coerce_string_list(
                raw_template["applicable_to"],
                context=f"counterfactual template {template_id!r} applicable_to",
            ),
            experiments=self._coerce_string_list(
                raw_template["experiments"],
                context=f"counterfactual template {template_id!r} experiments",
            ),
        )

    def _require_keys(
        self,
        mapping: dict[str, Any],
        keys: tuple[str, ...],
        context: str,
    ) -> None:
        missing = [key for key in keys if key not in mapping]
        if missing:
            missing_str = ", ".join(repr(key) for key in missing)
            raise ValueError(f"{context} is missing required key(s): {missing_str}")

    def _require_mapping(self, value: Any, context: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError(f"{context} must be a mapping")
        return copy.deepcopy(value)

    def _coerce_string_list(self, value: Any, context: str) -> list[str]:
        if not isinstance(value, list):
            raise ValueError(f"{context} must be a list")
        return [str(item) for item in value]

    def _render_template(
        self,
        template: str,
        values: dict[str, Any],
        context: str,
    ) -> str:
        missing: list[str] = []

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in values:
                missing.append(key)
                return match.group(0)
            return str(values[key])

        rendered = _PLACEHOLDER_RE.sub(replace, template)
        if missing:
            missing_names = ", ".join(f"{{{name}}}" for name in sorted(set(missing)))
            raise ValueError(
                f"{context} requires placeholder value(s) {missing_names}, "
                "but they were not provided"
            )
        return rendered

    def _parse_json_object(self, text: str, context: str) -> dict[str, Any]:
        raw = text.strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = extract_json_robust(raw)

        if parsed is None:
            snippet = raw[:200].replace("\n", " ")
            raise ValueError(f"Could not parse JSON object from {context}: {snippet!r}")
        if not isinstance(parsed, dict):
            raise ValueError(
                f"Expected {context} to return a JSON object, got {type(parsed).__name__}"
            )
        return parsed

    def _resolve_evidence_item(
        self,
        item: Any,
        mapping: dict[str, str],
    ) -> Any:
        if not isinstance(item, dict):
            return copy.deepcopy(item)

        resolved_item = copy.deepcopy(item)
        supports = resolved_item.get("supports")
        if isinstance(supports, list):
            resolved_item["supports"] = [mapping.get(name, name) for name in supports]
        return resolved_item


__all__ = ["CFTemplate", "PromptLoader", "TaskPrompt"]
