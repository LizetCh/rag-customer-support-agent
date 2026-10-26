# RAG Customer Support Agent

A RAG-powered, tool-using customer-support agent, demonstrated on a fictitious small bakery. It answers customer questions from the bakery's own documents (FAQ, hours, shipping, returns, allergens), checks live inventory, and hands off to a human when it can't resolve something -- built as a portfolio project demonstrating retrieval-augmented generation, an agent that calls tools (LangGraph), evaluation of both retrieval and tool choice, cost/latency observability, and a real deploy.

**Status:** environment setup. No live API yet -- see [PROGRESS.md](PROGRESS.md) for exactly where the project stands, and [CLAUDE.md](CLAUDE.md) for the full brief and roadmap.

## Architecture

```
Client -> POST /chat (FastAPI) -> LangGraph agent (Gemini)
                                     |
                 +-------------------+-------------------+
                 |                   |                   |
          search_knowledge     check_stock        handoff_to_human
          (pgvector RAG,       (SQL on the         (flags session
           Supabase)            products table)     as escalated)
                 |                   |                   |
                 +-------------------+-------------------+
                                     |
                         Gemini generates the reply
                                     |
                      response + logged tokens/cost/latency
```

## Tech stack

FastAPI - LangGraph - Gemini (`gemini-2.5-flash` chat, `gemini-embedding-001` embeddings) - Supabase/pgvector - Docker - Render.

## Getting started

```bash
uv sync
cp .env.example .env   # fill in your own Gemini + Supabase credentials
uv run uvicorn app.main:app --reload
uv run pytest -q
```

Credentials setup (step-by-step guides live in the project chat/sessions, not here yet):
1. Create a Gemini API key at [Google AI Studio](https://aistudio.google.com/).
2. Create a Supabase project, enable the `pgvector` extension, and run `supabase/schema.sql` in its SQL editor.

## Evaluation results

Not available yet -- filled in during Historia 3, with real recall@3 and tool-choice accuracy numbers (no placeholders).
