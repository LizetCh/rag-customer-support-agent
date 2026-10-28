from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000)
    # Omit on the first message; the server creates one and returns it.
    session_id: UUID | None = None


class ChatResponse(BaseModel):
    session_id: UUID
    reply: str
    tools_used: list[str]
    escalated: bool
