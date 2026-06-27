"""Rate limiting tests."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


def test_health_not_rate_limited():
    """Health endpoint should not be rate limited."""
    client = TestClient(app)
    for _ in range(100):
        r = client.get("/health")
        assert r.status_code == 200
