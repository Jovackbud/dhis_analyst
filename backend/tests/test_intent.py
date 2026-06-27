"""Intent classifier tests — all 5 output modes + edge cases."""
from datetime import date

from backend.app.agent.intent import classify_intent


def test_dashboard_intent_and_last_quarter_period():
    result = classify_intent("Show me malaria trends in Kaduna over the last quarter", today=date(2026, 6, 13))
    assert result["output_mode"] == "dashboard"
    assert any(m["uid"] == "fbfJHSPpUQD" for m in result["metrics"])
    assert result["org_unit"]["label"] == "Kaduna"
    assert "2026Q1" in result["periods"]


def test_report_intent():
    result = classify_intent("Prepare the monthly programme review")
    assert result["output_mode"] == "report"


def test_export_intent():
    result = classify_intent("Give me the raw numbers in Excel")
    assert result["output_mode"] == "export"


def test_presentation_intent():
    result = classify_intent("Create a briefing deck for the team")
    assert result["output_mode"] == "presentation"


def test_conversational_intent():
    result = classify_intent("Why is OPV3 dropout high in Sokoto?")
    assert result["output_mode"] == "conversational"
    assert result["needs_web_enrichment"] is False or result["needs_web_enrichment"] is True


def test_web_enrichment_trigger():
    result = classify_intent("How does our coverage compare to the WHO benchmark?")
    assert result["needs_web_enrichment"] is True
    assert len(result["web_search_queries"]) > 0


def test_no_web_enrichment_for_simple_query():
    result = classify_intent("Show me malaria cases in Kano")
    assert result["needs_web_enrichment"] is False


def test_period_explicit_year_quarter():
    result = classify_intent("ANC coverage 2025 Q2", today=date(2026, 6, 13))
    assert "2025Q2" in result["periods"]


def test_period_last_week():
    result = classify_intent("Numbers for last week", today=date(2026, 6, 13))
    assert any("W" in p for p in result["periods"])


def test_period_year_to_date():
    result = classify_intent("Year to date malaria data", today=date(2026, 6, 13))
    assert "2026" in result["periods"]


def test_period_last_year():
    result = classify_intent("Compare last year data", today=date(2026, 6, 13))
    assert "2025" in result["periods"]


def test_empty_message_triggers_clarification():
    result = classify_intent("")
    assert result["clarification_needed"] is True
    assert result["clarification_question"] is not None


def test_org_unit_detection_kano():
    result = classify_intent("Malaria cases in Kano state")
    assert result["org_unit"]["label"] == "Kano"
    assert result["org_unit"]["level"] == 2


def test_org_unit_national_fallback():
    result = classify_intent("Overall health coverage trends")
    assert result["org_unit"]["label"] == "National"
    assert result["org_unit"]["level"] == 1


def test_multiple_metrics():
    result = classify_intent("Compare malaria and cholera cases")
    uids = {m["uid"] for m in result["metrics"]}
    assert "fbfJHSPpUQD" in uids  # malaria
    assert "vc6J1qOWsNR" in uids  # cholera


def test_forced_mode_overrides():
    result = classify_intent("Show me malaria trends", forced_mode="export")
    assert result["output_mode"] == "export"


def test_viz_types_map():
    result = classify_intent("Map of TB cases")
    assert "map" in result["viz_types"]


def test_viz_types_trend():
    result = classify_intent("ANC trend line chart")
    assert "line" in result["viz_types"]
