"""Agent stream tests — all output modes + clarification."""
import pytest

from backend.config import Settings
from backend.app.agent.graph import run_agent_stream
from backend.app.models import ChatRequest, Identity


def _settings():
    return Settings(llm_provider="mock", embedding_provider="mock")


def _identity():
    return Identity(user_id="test_user", role="dhis2_user")


@pytest.mark.asyncio
async def test_dashboard_stream():
    request = ChatRequest(message="Show me malaria trends in Kaduna", output_mode="dashboard")
    events = []
    async for item in run_agent_stream(request, _settings(), _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: chart_config" in joined
    assert "event: done" in joined


@pytest.mark.asyncio
async def test_conversational_stream():
    request = ChatRequest(message="Tell me about ANC coverage in Nigeria")
    events = []
    async for item in run_agent_stream(request, _settings(), _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: token" in joined
    assert "event: done" in joined


@pytest.mark.asyncio
async def test_report_stream():
    request = ChatRequest(message="Prepare the monthly programme review for malaria", output_mode="report")
    events = []
    async for item in run_agent_stream(request, _settings(), _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: report_html" in joined
    assert "event: done" in joined


@pytest.mark.asyncio
async def test_presentation_stream():
    request = ChatRequest(message="Create a briefing deck for OPV3", output_mode="presentation")
    events = []
    async for item in run_agent_stream(request, _settings(), _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: slide_manifest" in joined
    assert "event: done" in joined


@pytest.mark.asyncio
async def test_export_stream():
    request = ChatRequest(message="Give me raw numbers in Excel for cholera", output_mode="export")
    events = []
    async for item in run_agent_stream(request, _settings(), _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: data_ready" in joined
    assert "event: done" in joined


@pytest.mark.asyncio
async def test_evidence_emitted_when_fusion_enabled():
    settings = _settings()
    settings.evidence_fusion = True
    request = ChatRequest(message="Show me malaria trends in Kaduna", output_mode="dashboard")
    events = []
    async for item in run_agent_stream(request, settings, _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: evidence" in joined


@pytest.mark.asyncio
async def test_no_evidence_when_fusion_disabled():
    settings = _settings()
    settings.evidence_fusion = False
    request = ChatRequest(message="Show me malaria trends", output_mode="dashboard")
    events = []
    async for item in run_agent_stream(request, settings, _identity()):
        events.append(item)
    joined = "".join(events)
    assert "event: evidence" not in joined
