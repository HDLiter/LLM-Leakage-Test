"""Display utilities for Jupyter notebooks.

Provides rich HTML/Markdown rendering for LLM responses, text comparisons,
and probe results.
"""

from __future__ import annotations

import json
import re

from IPython.display import HTML, Markdown, display


def strip_markdown_json(raw: str) -> str:
    """Strip markdown code fences and extract clean text/JSON."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()


def show_parsed_prediction(raw: str) -> str:
    """Extract JSON from raw LLM response and format as readable prediction text."""
    text = strip_markdown_json(raw)
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                data = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return text[:300]
        else:
            return text[:300]

    # 5-bin format
    if "strong_bear" in data:
        dist = [data.get(k, 0) for k in ["strong_bear", "weak_bear", "neutral", "weak_bull", "strong_bull"]]
        total = sum(dist)
        if total > 0:
            bull = (dist[3] + dist[4]) / total
            bear = (dist[0] + dist[1]) / total
        else:
            bull = bear = 0.2
        if bull > bear + 0.1:
            arrow, direction = "\u2191", "看涨"
        elif bear > bull + 0.1:
            arrow, direction = "\u2193", "看跌"
        else:
            arrow, direction = "\u2192", "中性"
        conf = max(bull, bear, (dist[2] / total) if total > 0 else 0.2)
        reasoning = data.get("reasoning", "")
        summary = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
        return f"{arrow} {direction} | 置信度: {conf:.0%} | {summary}"

    # binary format
    if "direction" in data:
        d = data["direction"]
        arrow = "\u2191" if d == "up" else ("\u2193" if d == "down" else "\u2192")
        reasoning = data.get("reasoning", "")
        summary = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
        return f"{arrow} {d} | {summary}"

    # scalar format
    if "score" in data:
        s = float(data["score"])
        arrow = "\u2191" if s > 0.1 else ("\u2193" if s < -0.1 else "\u2192")
        reasoning = data.get("reasoning", "")
        summary = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
        return f"{arrow} score={s:.2f} | {summary}"

    return text[:300]


def show_counterfactual_result(
    case_id: str,
    original_text: str,
    cf_text: str,
    orig_raw: str,
    cf_raw: str,
    variant_type: str,
) -> None:
    """Display a counterfactual attack result card with input comparison and parsed predictions."""
    orig_pred = show_parsed_prediction(orig_raw)
    cf_pred = show_parsed_prediction(cf_raw)

    html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; margin:10px 0; font-size:13px; overflow:hidden;">
        <div style="background:#e3f2fd; padding:8px 12px; font-weight:bold;">
            [{case_id}] {variant_type}
        </div>
        <table style="width:100%; border-collapse:collapse;">
        <tr style="background:#f5f5f5;">
            <th style="width:50%; padding:6px 10px; border:1px solid #ddd; text-align:left;">原始新闻</th>
            <th style="width:50%; padding:6px 10px; border:1px solid #ddd; text-align:left;">反事实新闻</th>
        </tr>
        <tr>
            <td style="padding:8px 10px; border:1px solid #ddd; vertical-align:top; white-space:pre-wrap; max-height:150px; overflow-y:auto;">{original_text[:300]}</td>
            <td style="padding:8px 10px; border:1px solid #ddd; vertical-align:top; white-space:pre-wrap; max-height:150px; overflow-y:auto;">{cf_text[:300]}</td>
        </tr>
        <tr style="background:#f5f5f5;">
            <th style="padding:6px 10px; border:1px solid #ddd; text-align:left;">原始预测</th>
            <th style="padding:6px 10px; border:1px solid #ddd; text-align:left;">反事实预测</th>
        </tr>
        <tr>
            <td style="padding:8px 10px; border:1px solid #ddd; vertical-align:top;">{orig_pred}</td>
            <td style="padding:8px 10px; border:1px solid #ddd; vertical-align:top;">{cf_pred}</td>
        </tr>
        </table>
    </div>
    """
    display(HTML(html))


def show_llm_response(label: str, text: str, max_len: int = 800) -> None:
    """Display an LLM response in a styled Markdown block."""
    truncated = text[:max_len] + "..." if len(text) > max_len else text
    display(Markdown(f"**{label}**\n\n```\n{truncated}\n```"))


def show_comparison(original: str, modified: str, title: str = "") -> None:
    """Side-by-side HTML table comparing original and modified text."""
    header = f"<h4>{title}</h4>" if title else ""
    html = f"""
    {header}
    <table style="width:100%; border-collapse:collapse; font-size:13px;">
    <tr style="background:#f0f0f0;">
        <th style="width:50%; padding:8px; border:1px solid #ddd; text-align:left;">原文</th>
        <th style="width:50%; padding:8px; border:1px solid #ddd; text-align:left;">修改后</th>
    </tr>
    <tr>
        <td style="padding:8px; border:1px solid #ddd; vertical-align:top; white-space:pre-wrap;">{original}</td>
        <td style="padding:8px; border:1px solid #ddd; vertical-align:top; white-space:pre-wrap;">{modified}</td>
    </tr>
    </table>
    """
    display(HTML(html))


def show_probe_result(
    probe_id: str,
    question: str,
    ground_truth: str,
    model_answer: str,
    score: float | None,
) -> None:
    """Display a complete memorization probe result."""
    score_color = "#4CAF50" if score == 1.0 else ("#FF9800" if score == 0.5 else "#F44336")
    score_text = f"{score}" if score is not None else "N/A"
    html = f"""
    <div style="border:1px solid #ddd; border-radius:6px; padding:12px; margin:8px 0; font-size:13px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong>[{probe_id}]</strong>
            <span style="background:{score_color}; color:white; padding:2px 10px; border-radius:12px; font-size:12px;">
                Score: {score_text}
            </span>
        </div>
        <div style="margin-bottom:6px;"><strong>Q:</strong> {question}</div>
        <div style="margin-bottom:6px; color:#666;"><strong>标准答案:</strong> {ground_truth}</div>
        <div style="background:#f8f8f8; padding:8px; border-radius:4px; white-space:pre-wrap;"><strong>模型回答:</strong><br/>{model_answer}</div>
    </div>
    """
    display(HTML(html))


def show_timeliness_leakage(
    case_id: str,
    news_title: str,
    news_date: str,
    news_content: str,
    response_text: str,
    evidence: list[str],
    known_outcome: str,
    outcome_date: str,
    severity: str,
) -> None:
    """Display a timeliness leakage case as a rich HTML card.

    Highlights evidence phrases in the model response and shows the
    known future outcome for comparison.
    """
    sev_color = "#F44336" if severity == "major" else ("#FF9800" if severity == "minor" else "#4CAF50")
    sev_label = severity.upper()

    # Highlight evidence in response text
    highlighted = response_text
    for phrase in evidence:
        highlighted = highlighted.replace(
            phrase,
            f'<mark style="background:#FFEB3B;padding:0 2px;">{phrase}</mark>',
        )

    evidence_items = "".join(f"<li>{e}</li>" for e in evidence) if evidence else "<li>（无）</li>"

    html = f"""
    <div style="border:2px solid {sev_color}; border-radius:8px; margin:12px 0; font-size:13px; overflow:hidden;">
        <div style="background:{sev_color}; color:white; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
            <strong>[{case_id}] {news_title}</strong>
            <span style="background:white; color:{sev_color}; padding:2px 10px; border-radius:12px; font-weight:bold; font-size:12px;">{sev_label}</span>
        </div>
        <div style="padding:12px 14px;">
            <div style="margin-bottom:10px;">
                <div style="font-weight:bold; color:#555; margin-bottom:4px;">原始新闻 ({news_date})</div>
                <div style="background:#f8f8f8; padding:8px; border-radius:4px; white-space:pre-wrap; max-height:200px; overflow-y:auto;">{news_content}</div>
            </div>
            <div style="margin-bottom:10px;">
                <div style="font-weight:bold; color:#555; margin-bottom:4px;">模型分析</div>
                <div style="background:#f8f8f8; padding:8px; border-radius:4px; white-space:pre-wrap; max-height:300px; overflow-y:auto;">{highlighted}</div>
            </div>
            <div style="margin-bottom:10px;">
                <div style="font-weight:bold; color:#555; margin-bottom:4px;">泄露证据</div>
                <ul style="margin:4px 0; padding-left:20px;">{evidence_items}</ul>
            </div>
            <div style="background:#FFF3E0; padding:8px; border-radius:4px; border-left:4px solid #FF9800;">
                <div style="font-weight:bold; color:#E65100; margin-bottom:4px;">已知后续结果 ({outcome_date})</div>
                <div>{known_outcome}</div>
            </div>
        </div>
    </div>
    """
    display(HTML(html))
