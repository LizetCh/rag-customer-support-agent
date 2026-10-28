"""Input validation for POST /chat. These requests are rejected before the
agent runs, so they make no Gemini or Supabase calls."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rejects_blank_message() -> None:
    assert client.post("/chat", json={"message": "   "}).status_code == 422


def test_rejects_oversized_message() -> None:
    assert client.post("/chat", json={"message": "a" * 2001}).status_code == 422


def test_rejects_non_uuid_session_id() -> None:
    response = client.post("/chat", json={"message": "hi", "session_id": "session-1"})
    assert response.status_code == 422
