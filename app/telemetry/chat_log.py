"""Per-turn telemetry: tokens, estimated cost, and latency, saved to chat_logs.

Message text is deliberately not stored: customers can type personal data into
a public chat, and these metrics don't need it.
"""

import logging
from collections.abc import Sequence
from uuid import UUID

from langchain_core.messages import BaseMessage

from app.db.client import get_client

logger = logging.getLogger(__name__)

# gemini-3.6-flash, Standard tier, USD per 1M tokens, from Google's pricing page
# on 2026-11-02. Both prices double on 2027-01-01.
INPUT_USD_PER_MILLION = 0.75
OUTPUT_USD_PER_MILLION = 3.75


def count_tokens(messages: Sequence[BaseMessage]) -> tuple[int, int]:
    # A turn with a tool makes two Gemini calls and both are billed, so sum them.
    usages = [m.usage_metadata for m in messages if m.type == "ai" and m.usage_metadata]
    return sum(u["input_tokens"] for u in usages), sum(u["output_tokens"] for u in usages)


def estimate_cost(tokens_in: int, tokens_out: int) -> float:
    # What the turn would cost on the paid tier. Excludes the search_knowledge
    # embedding call and any cache discount.
    cost = tokens_in * INPUT_USD_PER_MILLION + tokens_out * OUTPUT_USD_PER_MILLION
    return round(cost / 1_000_000, 6)


def log_turn(
    session_id: UUID,
    turn_messages: Sequence[BaseMessage],
    tools_used: list[str],
    latency_ms: int,
    escalated: bool,
) -> None:
    tokens_in, tokens_out = count_tokens(turn_messages)
    # Telemetry must never cost the customer their reply, so report the failure
    # and carry on. Any exception counts: database, network, or client errors.
    try:
        get_client().table("chat_logs").insert(
            {
                "session_id": str(session_id),
                "tool_used": ", ".join(tools_used) or None,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "estimated_cost_usd": estimate_cost(tokens_in, tokens_out),
                "latency_ms": latency_ms,
                "escalated": escalated,
            }
        ).execute()
    except Exception:
        logger.exception("Failed to write chat_logs row for session %s", session_id)
