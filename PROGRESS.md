# Progress

Read this file first, every session, on either laptop. It is more precise than CLAUDE.md's roadmap checklist: it says exactly what is done and what the very next step is.

## Current status

- **Active Historia:** Historia 2 -- Agent with tools (Historia 1 is fully done and checked off).
- **Next concrete step:** Start Historia 2 / Task 1 by explaining agents, tool calling, and a LangGraph state graph in plain language, *then* build the graph with three tools: `search_knowledge` (wraps `app/rag/search.py`), `check_stock` (needs the `products` table seeded first -- no seed script exists yet), and `handoff_to_human`. DoD: on 3 test questions, one per tool, the agent picks the right tool each time.
- **Blocked on:** nothing.
- **Setup notes:** `.env` must exist on each laptop (gitignored; copy from `.env.example` and fill it in). Supabase's Data API must be enabled (Project Settings -> Data API) -- it had been switched off, which caused the earlier `503 PGRST002`. `scripts/verify_setup.py` checks Supabase and Gemini.
- **GitHub remote:** connected -- https://github.com/LizetCh/rag-customer-support-agent
- **Last session:** 2026-10-26 (second session, on the Mac)

## Session log (most recent first)

### 2026-10-26 (second session, Mac) -- Historia 1 complete
- Created `.env` on the Mac. Fixed a `401 Invalid API key` (the wrong value had been pasted as `SUPABASE_SERVICE_ROLE_KEY`).
- Found the real cause of the earlier `503 PGRST002`: the Supabase Data API had been switched off. Turned it on; `verify_setup.py` now passes for Supabase and Gemini.
- Enabled RLS on all 3 tables (appended to `supabase/schema.sql` and run in the SQL editor). No policies, so the `anon` key has no access; the server's `service_role` key bypasses RLS.
- Wrote 6 fictitious "Hearth & Crumb Bakery" docs under `docs/`, one topic per file so each eval question maps to one source document. Stock is deliberately *not* in the docs (that is `check_stock`'s job).
- Built ingestion: `app/rag/chunking.py` (split at `## ` headings, prefix each chunk with "<title> > <section>"), `app/rag/embeddings.py`, `app/db/client.py`, `scripts/ingest.py` (idempotent: deletes a doc's old chunks before inserting). 38 chunks ingested, 768-dim vectors confirmed.
- Built `app/rag/search.py` (`search(question, k=3)`, runnable via `python -m app.rag.search "..."`). No similarity threshold yet: good matches score about 0.68 and irrelevant ones about 0.60, so the cutoff will come from eval data in Historia 3.
- Idea for Historia 3 / README: compare recall@3 for structure-aware vs fixed-size chunking.
- Explained: schema cache, RLS, chunking strategies, embeddings, embedding spaces (vectors from different models are incompatible), top-k and hallucination risk, RPC. All added to GLOSSARY.md.

### 2026-10-26 -- Environment setup
- Wrote CLAUDE.md (project brief, tech stack, architecture, roadmap, working agreement, session start/end protocol) and this PROGRESS.md.
- Scaffolded the repo: app/ package (main.py with /health, config.py, empty db/rag/agent/api/telemetry subpackages), tests/test_health.py, docs/ scripts/ evals/ supabase/ folders, .env.example, .gitignore, README.md, GLOSSARY.md, supabase/schema.sql.
- Decisions made: uv-managed Python 3.12 venv (not 3.14, for broader wheel compatibility with langgraph/langchain-google-genai/supabase); gemini-2.5-flash as the default chat model and gemini-embedding-001 at 768 dims as the default embedding model, chosen for low cost since Historia 3 tracks cost per request; everything in English including the fictitious bakery content.
- Project renamed from "bread-agent" to **rag-customer-support-agent** (pyproject.toml, README.md, CLAUDE.md title) so the GitHub repo name itself communicates the skills demonstrated to a hiring manager scanning repo names. Local folder on this machine stays `bread-agent` (Windows locked a rename -- a leftover uvicorn/python process was holding the directory; killed those, but the directory itself still reported busy, so left it as-is since it's cosmetic only and not worth forcing).
- Connected the GitHub remote (https://github.com/LizetCh/rag-customer-support-agent) and pushed both the scaffold commit and the rename commit.
- User added the Gemini API key and ran supabase/schema.sql in the Supabase SQL editor (success, no errors; all 3 tables confirmed visible in Table Editor).
- Wrote scripts/verify_setup.py to sanity-check both credentials without ever printing the secrets, just pass/fail. Needs `PYTHONPATH=.` to run (app/ isn't installed as a package) -- same reason pytest needed `pythonpath = ["."]` added to pyproject.toml's `[tool.pytest.ini_options]`.
- Supabase check kept failing with 503 PGRST002. Isolated it to a server-side issue (not our code/keys) via a raw curl straight to the REST API, bypassing supabase-py -- same error. Project restart (Settings -> General) did not resolve it either.
- Session ended here, mid-troubleshooting, without a working Supabase connection and without ever reaching the Gemini check. No bakery content, no RAG/agent code yet.
