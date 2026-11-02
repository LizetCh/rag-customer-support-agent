from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_serves_the_chat_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Hearth &amp; Crumb Bakery" in response.text


def test_chat_page_is_left_out_of_the_api_docs() -> None:
    assert "/" not in client.get("/openapi.json").json()["paths"]
