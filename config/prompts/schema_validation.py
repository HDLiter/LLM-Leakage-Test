from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Install with: "
        "conda run -n rag_finance python -m pip install pyyaml"
    ) from exc

ROOT = Path(__file__).resolve().parent
TASK_CATALOG = ROOT / "task_prompts.yaml"
COUNTERFACTUAL_CATALOG = ROOT / "counterfactual_templates.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json_input(source: str):
    if source == "-":
        return json.load(sys.stdin)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def is_type(value, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_schema(schema: dict, data, path: str = "root") -> list[str]:
    errors: list[str] = []

    schema_type = schema.get("type")
    if schema_type and not is_type(data, schema_type):
        return [f"{path}: expected {schema_type}, got {type(data).__name__}"]

    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, got {data!r}")

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']}, got {data!r}")

    if schema_type == "object" and isinstance(data, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in data:
                errors.append(f"{path}.{key}: missing required field")

        if schema.get("additionalProperties", True) is False:
            for key in data:
                if key not in properties:
                    errors.append(f"{path}.{key}: unexpected field")

        for key, value in data.items():
            if key in properties:
                errors.extend(validate_schema(properties[key], value, f"{path}.{key}"))

    elif schema_type == "array" and isinstance(data, list):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if min_items is not None and len(data) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(data)}")
        if max_items is not None and len(data) > max_items:
            errors.append(f"{path}: expected at most {max_items} items, got {len(data)}")

        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(data):
                errors.extend(validate_schema(item_schema, item, f"{path}[{idx}]"))

    elif schema_type == "string" and isinstance(data, str):
        min_len = schema.get("minLength")
        max_len = schema.get("maxLength")
        if min_len is not None and len(data) < min_len:
            errors.append(f"{path}: expected length >= {min_len}, got {len(data)}")
        if max_len is not None and len(data) > max_len:
            errors.append(f"{path}: expected length <= {max_len}, got {len(data)}")

    elif schema_type in {"integer", "number"} and not isinstance(data, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and data < minimum:
            errors.append(f"{path}: expected >= {minimum}, got {data}")
        if maximum is not None and data > maximum:
            errors.append(f"{path}: expected <= {maximum}, got {data}")

    return errors


def resolve_task_schema(catalog: dict, prompt_id: str) -> tuple[dict, dict]:
    prompt = catalog["prompts"].get(prompt_id)
    if prompt is None:
        raise KeyError(f"Unknown task prompt id: {prompt_id}")

    if "output_schema" in prompt:
        return prompt, prompt["output_schema"]

    ref = prompt.get("output_schema_ref")
    if not ref:
        raise KeyError(f"Prompt {prompt_id} does not define an output schema")
    return prompt, catalog["common_schemas"][ref]


def resolve_counterfactual_schema(catalog: dict, template_id: str) -> tuple[dict, dict]:
    template = catalog["templates"].get(template_id)
    if template is None:
        raise KeyError(f"Unknown counterfactual template id: {template_id}")

    if "output_schema" in template:
        return template, template["output_schema"]

    ref = template.get("output_schema_ref")
    if not ref:
        raise KeyError(f"Template {template_id} does not define an output schema")
    return template, catalog["common_schemas"][ref]


def validate_slot_semantics(prompt: dict, data: dict) -> list[str]:
    errors: list[str] = []
    semantics = prompt.get("slot_semantics", {})
    for slot_name, spec in semantics.items():
        if slot_name not in data:
            continue
        allowed = spec.get("allowed_values")
        if allowed and data[slot_name] not in allowed:
            errors.append(
                f"root.{slot_name}: expected one of {allowed}, got {data[slot_name]!r}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", choices=["task", "counterfactual"], required=True)
    parser.add_argument("--id", required=True, help="Prompt id or template id")
    parser.add_argument("--json", required=True, help="JSON file path or - for stdin")
    args = parser.parse_args()

    payload = load_json_input(args.json)

    if args.catalog == "task":
        catalog = load_yaml(TASK_CATALOG)
        prompt, schema = resolve_task_schema(catalog, args.id)
        errors = validate_schema(schema, payload)
        errors.extend(validate_slot_semantics(prompt, payload))
    else:
        catalog = load_yaml(COUNTERFACTUAL_CATALOG)
        _, schema = resolve_counterfactual_schema(catalog, args.id)
        errors = validate_schema(schema, payload)

    if errors:
        print("INVALID")
        for err in errors:
            print(f"- {err}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
