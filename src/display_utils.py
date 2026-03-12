"""Display utilities for Jupyter notebooks.

Provides rich HTML/Markdown rendering for LLM responses, text comparisons,
and probe results.
"""

from __future__ import annotations

from IPython.display import HTML, Markdown, display


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
