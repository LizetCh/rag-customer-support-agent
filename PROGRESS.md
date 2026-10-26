# Progress

Read this file first, every session, on either laptop. It is more precise than CLAUDE.md's roadmap checklist: it says exactly what is done and what the very next step is.

## Current status

- **Active Historia:** Setup (pre-Historia 1)
- **Next concrete step:** First re-run `PYTHONPATH=. uv run python scripts/verify_setup.py` to check whether Supabase's API has recovered. If it passes, move straight to Historia 1 / Task 1 -- write the bakery's docs/*.md files (FAQ, hours, shipping, returns, allergens) together. If it's still failing, check status.supabase.com for incidents, and consider recreating the Supabase project (current one may be stuck) -- re-run supabase/schema.sql in the new project either way.
- **Blocked on:** Supabase's REST API (PostgREST) is returning `503 PGRST002 "Could not query the database for the schema cache"` for this project. Confirmed via a raw `curl` straight to `$SUPABASE_URL/rest/v1/...` (bypassing supabase-py entirely) -- same error, so it is NOT our code or credentials. The tables (document_chunks, products, chat_logs) do exist (visible in Table Editor), schema.sql ran with no errors, project shows "Active," and a full project restart did not fix it. This looks like a server-side infra issue on Supabase's end for this specific project.
- **Gemini key:** added to `.env`, but not yet actually verified with a real call -- `scripts/verify_setup.py` checks Supabase first and never reached the Gemini check. Verify that too once Supabase is unblocked.
- **GitHub remote:** connected and pushed -- https://github.com/LizetCh/rag-customer-support-agent
- **Last session:** 2026-10-26

## Session log (most recent first)

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
