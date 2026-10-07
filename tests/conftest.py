import pytest


@pytest.fixture(autouse=True)
def no_real_gemini_key(monkeypatch):
    """Make sure tests never call the real Gemini API."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)