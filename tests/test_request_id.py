"""Correlation IDs: every response carries one, and a request's log lines share it."""

import logging
from unittest.mock import MagicMock
from uuid import UUID

from fastapi.testclient import TestClient
from langchain_core.exceptions import ModelError

from app.api import chat as chat_module
from app.main import app
from app.telemetry.request_id import RequestIdFilter

client = TestClient(app)


def test_generates_a_uuid_when_the_client_sends_none() -> None:
    response = client.get("/health")
    UUID(response.headers["X-Request-ID"])


def test_reuses_a_safe_client_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_replaces_an_unsafe_client_id() -> None:
    # A newline could forge a fake log line, and a huge value bloats every log.
    for unsafe in ["abc\nFAKE LOG LINE", "a" * 65, "has space"]:
        response = client.get("/health", headers={"X-Request-ID": unsafe})
        UUID(response.headers["X-Request-ID"])


def test_every_log_line_of_a_request_carries_its_id(monkeypatch, caplog) -> None:
    caplog.handler.addFilter(RequestIdFilter())
    graph = MagicMock()
    graph.invoke.side_effect = ModelError("quota")
    monkeypatch.setattr(chat_module, "graph", graph)

    with caplog.at_level(logging.INFO, logger="app"):
        response = client.post("/chat", json={"message": "hi"}, headers={"X-Request-ID": "trace-me"})

    assert response.status_code == 503
    assert response.headers["X-Request-ID"] == "trace-me"
    messages = [r.getMessage() for r in caplog.records]
    assert any("Gemini call failed" in m for m in messages)
    assert any("POST /chat -> 503" in m for m in messages)
    assert {r.request_id for r in caplog.records} == {"trace-me"}
