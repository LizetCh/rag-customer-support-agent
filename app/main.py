from fastapi import FastAPI

app = FastAPI(title="Bakery Support Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
