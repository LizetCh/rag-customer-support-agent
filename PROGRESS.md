# Progress

Read this file first, every session, on either laptop. It is more precise than CLAUDE.md's roadmap checklist: it says exactly what is done and what the very next step is.

## Current status

- **Active Historia:** Setup (pre-Historia 1)
- **Next concrete step:** Verify the scaffold (pytest + uvicorn smoke test), commit, then start Historia 1 / Task 1 -- write the bakery's docs/*.md files (FAQ, hours, shipping, returns, allergens) together.
- **Blocked on:** nothing yet. Still need to create a Gemini API key (Google AI Studio) and a Supabase project before Historia 1's ingestion script can run -- guided walkthrough pending.
- **GitHub remote:** not connected yet. User will create the repo on GitHub and share the URL.
- **Last session:** 2026-10-26

## Session log (most recent first)

### 2026-10-26 -- Environment setup
- Wrote CLAUDE.md (project brief, tech stack, architecture, roadmap, working agreement, session start/end protocol) and this PROGRESS.md.
- Scaffolded the repo: app/ package (main.py with /health, config.py, empty db/rag/agent/api/telemetry subpackages), tests/test_health.py, docs/ scripts/ evals/ supabase/ folders, .env.example, .gitignore, README.md, GLOSSARY.md, supabase/schema.sql.
- Decisions made: uv-managed Python 3.12 venv (not 3.14, for broader wheel compatibility with langgraph/langchain-google-genai/supabase); gemini-2.5-flash as the default chat model and gemini-embedding-001 at 768 dims as the default embedding model, chosen for low cost since Historia 3 tracks cost per request; everything in English including the fictitious bakery content.
- Not done yet: no real Gemini/Supabase credentials, no GitHub remote, no bakery content, no RAG/agent code.
