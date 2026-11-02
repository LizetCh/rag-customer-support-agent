"""Telemetry maths and the /chat wiring. Gemini and Supabase are faked, so these
tests make no network calls."""

from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from langchain_core.exceptions import ModelError
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.api import chat as chat_module
from app.main import app
from app.telemetry import chat_log


def ai(text: str, tokens_in: int, tokens_out: int) -> AIMessage:
    return AIMessage(
        text,
        usage_metadata={
            "input_tokens": tokens_in,
            "output_tokens": tokens_out,
            "total_tokens": tokens_in + tokens_out,
        },
    )


def test_count_tokens_sums_every_gemini_call_in_the_turn() -> None:
    messages = [
        HumanMessage("Any baguettes?"),
        ai("", 100, 10),
        ToolMessage("Baguette: 4 in stock", tool_call_id="1", name="check_stock"),
        ai("Yes, 4 left.", 150, 20),
    ]
    assert chat_log.count_tokens(messages) == (250, 30)


def test_estimate_cost_uses_input_and_output_prices() -> None:
    assert chat_log.estimate_cost(1_000_000, 0) == 0.75
    assert chat_log.estimate_cost(0, 1_000_000) == 3.75
    assert chat_log.estimate_cost(1000, 100) == 0.001125


def test_log_turn_writes_metrics_without_message_text(monkeypatch) -> None:
    client = MagicMock()
    monkeypatch.setattr(chat_log, "get_client", lambda: client)
    session_id = uuid4()

    chat_log.log_turn(session_id, [ai("secret reply", 1000, 100)], ["check_stock"], 1234, False)

    client.table.assert_called_once_with("chat_logs")
    client.table.return_value.insert.assert_called_once_with(
        {
            "session_id": str(session_id),
            "tool_used": "check_stock",
            "tokens_in": 1000,
            "tokens_out": 100,
            "estimated_cost_usd": 0.001125,
            "latency_ms": 1234,
            "escalated": False,
        }
    )


def test_log_turn_survives_a_database_failure(monkeypatch, caplog) -> None:
    client = MagicMock()
    client.table.side_effect = RuntimeError("database down")
    monkeypatch.setattr(chat_log, "get_client", lambda: client)

    chat_log.log_turn(uuid4(), [], [], 1, False)

    assert "Failed to write chat_logs row" in caplog.text


def test_chat_logs_only_the_current_turn(monkeypatch) -> None:
    earlier_turn = [HumanMessage("Hi"), ai("Hello!", 500, 50)]
    current_turn = [HumanMessage("Any baguettes?"), ai("Yes.", 100, 10)]
    graph = MagicMock()
    graph.invoke.return_value = {"messages": earlier_turn + current_turn}
    log_turn = MagicMock()
    monkeypatch.setattr(chat_module, "graph", graph)
    monkeypatch.setattr(chat_module, "log_turn", log_turn)

    response = TestClient(app).post("/chat", json={"message": "Any baguettes?"})

    assert response.status_code == 200
    args = log_turn.call_args.args
    assert str(args[0]) == response.json()["session_id"]
    assert args[1] == current_turn
    assert args[2] == []
    assert args[3] >= 0
    assert args[4] is False


def test_chat_returns_503_without_details_when_gemini_fails(monkeypatch) -> None:
    graph = MagicMock()
    graph.invoke.side_effect = ModelError("secret internal detail")
    monkeypatch.setattr(chat_module, "graph", graph)

    response = TestClient(app).post("/chat", json={"message": "Any baguettes?"})

    assert response.status_code == 503
    assert "secret" not in response.text
