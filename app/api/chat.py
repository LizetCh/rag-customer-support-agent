from uuid import uuid4

from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.graph import build_graph
from app.agent.tools import handoff_to_human
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()

# In-memory conversation history: lost on restart, not shared between server
# instances, and unbounded. Fine locally; replace with Postgres before deploy.
graph = build_graph(checkpointer=InMemorySaver())


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    # Plain `def`: graph.invoke blocks on Gemini, so FastAPI runs it in a thread.
    session_id = request.session_id or uuid4()
    result = graph.invoke(
        {"messages": [HumanMessage(request.message)]},
        {"configurable": {"thread_id": str(session_id)}},
    )

    # The state holds the whole conversation; report only this turn's tools.
    messages = result["messages"]
    turn_start = max(i for i, m in enumerate(messages) if m.type == "human")
    tools_used = [m.name for m in messages[turn_start:] if m.type == "tool"]

    return ChatResponse(
        session_id=session_id,
        reply=messages[-1].text,
        tools_used=tools_used,
        escalated=handoff_to_human.name in tools_used,
    )
