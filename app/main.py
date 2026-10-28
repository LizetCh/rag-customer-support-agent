from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(title="Bakery Support Agent")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
