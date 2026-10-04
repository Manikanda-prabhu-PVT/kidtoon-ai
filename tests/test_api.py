from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sample_story_has_three_scenes():
    response = client.get("/story/sample")
    assert response.status_code == 200
    assert len(response.json()["scenes"]) == 3


def test_generate_returns_story_with_cleaned_prompt():
    response = client.post("/story/generate", json={"prompt": "   A rabbit story   "})
    assert response.status_code == 200
    assert response.json()["prompt"] == "A rabbit story"


def test_generate_rejects_blank_prompt():
    response = client.post("/story/generate", json={"prompt": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_generate_rejects_missing_prompt():
    response = client.post("/story/generate", json={})
    assert response.status_code == 422

def test_home_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "KidToon" in response.text