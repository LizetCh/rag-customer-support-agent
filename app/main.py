from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.chat import router as chat_router

CHAT_PAGE = Path(__file__).parent / "static" / "chat.html"

app = FastAPI(title="Bakery Support Agent")
app.include_router(chat_router)


@app.get("/", include_in_schema=False)
def chat_page() -> FileResponse:
    return FileResponse(CHAT_PAGE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
