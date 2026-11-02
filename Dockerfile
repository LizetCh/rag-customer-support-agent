FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.25 /uv /usr/local/bin/uv

WORKDIR /srv

# Dependencies first: Docker caches this layer until the lockfile changes.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app

# Least privilege: the server does not need root.
RUN useradd --create-home appuser
USER appuser

# Render sets PORT at runtime. exec lets uvicorn receive shutdown signals.
CMD ["sh", "-c", "exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
