import logging
import time
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from langchain_core.exceptions import ModelError
from langchain_core.messages import HumanMessage
from langchain_google_genai.chat_models import GoogleGenerativeAIError
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.graph import build_graph
from app.agent.tools import handoff_to_human
from app.api.schemas import ChatRequest, ChatResponse
from app.telemetry.chat_log import log_turn

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory conversation history: lost on restart and not shared between server
# instances. Fine for a single-server demo, and it keeps message text out of the
# database. Production would need a Postgres checkpointer with a retention policy.
graph = build_graph(checkpointer=InMemorySaver())


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    # Plain `def`: graph.invoke blocks on Gemini, so FastAPI runs it in a thread.
    # Deliberately public so recruiters can try the demo. Gemini's free-tier
    # quota bounds usage and cost; add auth or a cap before enabling billing.
    session_id = request.session_id or uuid4()
    started = time.perf_counter()
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(request.message)]},
            {"configurable": {"thread_id": str(session_id)}},
        )
    except (ModelError, GoogleGenerativeAIError):
        # Covers chat and embedding failures, including Gemini's own quota.
        logger.exception("Gemini call failed for session %s", session_id)
        raise HTTPException(503, "The assistant is unavailable right now. Please try again later.") from None
    latency_ms = round((time.perf_counter() - started) * 1000)

    # The state holds the whole conversation; report only this turn's messages.
    messages = result["messages"]
    turn_start = max(i for i, m in enumerate(messages) if m.type == "human")
    turn_messages = messages[turn_start:]
    tools_used = [m.name for m in turn_messages if m.type == "tool"]
    escalated = handoff_to_human.name in tools_used

    log_turn(session_id, turn_messages, tools_used, latency_ms, escalated)

    return ChatResponse(
        session_id=session_id,
        reply=messages[-1].text,
        tools_used=tools_used,
        escalated=escalated,
    )
