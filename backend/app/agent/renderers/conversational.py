from __future__ import annotations

import logging
from backend.app.agent.state import AgentState

logger = logging.getLogger("dhis2_analyst.renderer.conversational")


def render_answer(state: AgentState) -> str:
    """Build a rich conversational markdown response."""
    data = state.get("dhis2_data", {})
    headers = data.get("headers", [])
    rows = data.get("rows", [])
    metrics = state.get("metrics", [])
    metric = metrics[0]["label"] if metrics else "Health Indicator"
    org = state["org_unit"]["label"]
    periods = state.get("periods", [])
    period_text = ", ".join(periods)
    source = data.get("metadata", {}).get("data_source", "analytics_api")

    logger.info(
        "render_conversational_start",
        extra={
            "metric": metric,
            "org_unit": org,
            "periods": periods,
            "rows_count": len(rows),
        }
    )

    parts: list[str] = []

    # Title
    parts.append(f"## {metric} — {org}\n")

    # Summary
    values = []
    for row in rows:
        try:
            if len(row) > 2:
                values.append(float(row[2]))
        except (ValueError, TypeError):
            pass

    total = sum(values)
    parts.append(
        f"I retrieved **{len(rows)} data point{'s' if len(rows) != 1 else ''}** "
        f"from {source} for **{period_text}**.\n"
    )

    if values:
        parts.append(f"- **Total aggregate**: {total:,.0f}")
        parts.append(f"- **Average**: {total / len(values):,.1f}")
        parts.append(f"- **Min**: {min(values):,.0f} | **Max**: {max(values):,.0f}")

    # Trend analysis
    if len(values) >= 2:
        first, last = values[0], values[-1]
        if first > 0:
            pct = ((last - first) / first) * 100
            direction = "📈 increased" if pct > 0 else "📉 decreased"
            parts.append(
                f"\n**Trend**: {metric} {direction} by **{abs(pct):.1f}%** "
                f"from {periods[0]} to {periods[-1]}."
            )

    # Data table
    if rows:
        parts.append("\n### Data")
        parts.append(f"| {' | '.join(headers or ['Org Unit', 'Period', 'Value', 'Metric'])} |")
        parts.append(f"| {' | '.join(['---'] * len(headers or ['', '', '', '']))} |")
        for row in rows[:20]:
            cells = [str(c) for c in row]
            parts.append(f"| {' | '.join(cells)} |")
        if len(rows) > 20:
            parts.append(f"\n*Showing 20 of {len(rows)} rows. Use Export mode for full data.*")

    # Web context citations
    web_items = [c for c in state.get("web_context", []) if not c.get("url", "").startswith("local://")]
    if web_items:
        parts.append("\n### External Context")
        for item in web_items[:5]:
            parts.append(f"- [{item.get('title', 'Source')}]({item.get('url', '')})")

    # Evidence summary
    evidence = state.get("evidence_items", [])
    if evidence:
        parts.append("\n---")
        parts.append(f"*{len(evidence)} evidence source{'s' if len(evidence) != 1 else ''} tagged. "
                      f"Confidence range: {min(e['confidence'] for e in evidence):.0%}–{max(e['confidence'] for e in evidence):.0%}.*")

    result = "\n".join(parts)
    logger.info("render_conversational_complete", extra={"response_length": len(result)})
    return result
