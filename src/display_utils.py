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
    sev_color = "#F44336" if severity == "major" else "#FF9800"
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
