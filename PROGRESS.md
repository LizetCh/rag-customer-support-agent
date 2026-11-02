# Progress

Read this file first, every session, on either laptop. It is more precise than CLAUDE.md's roadmap checklist: it says exactly what is done and what the very next step is.

## Current status

- **Active Historia:** Historia 4 -- Deploy is complete, at https://rag-customer-support-agent-f85i.onrender.com. A real /chat turn on the public URL returned a good reply and wrote a `chat_logs` row (2026-11-02, 21:35 UTC).
- **Next concrete step:** add a demo video or screenshots to the README, since the free-tier demo can run out of quota. Historia 5 (the optional visualizer) is the only roadmap item left, and it starts only if the user wants it. The user stays on the Gemini free tier. The app now has its own AI Studio project, so other projects no longer share its quota.
- **Model note:** `gemini-3.6-flash` ignores `temperature` ("uses fixed sampling defaults"), so `temperature=0` in `get_llm` has no effect and eval results can vary between runs.
- **Free-tier limits hit on 2026-10-28:** chat = 5 requests/min and 20/day (one full tool-choice run uses all 20); embeddings also return 429 after a few quick back-to-back eval runs. The configured `gemini-3.5-flash` is billed as `gemini-3.6-flash` (alias redirect), so the chat model is now pinned to `gemini-3.6-flash` (default, `.env.example`, and the user's `.env`).
- **Ideas parked for Historia 3 evals:** (1) compare recall@3 for dense-only vs hybrid search (pgvector + Postgres full-text, fused with RRF); (2) compare structure-aware vs fixed-size chunking; (3) include ambiguous tool-choice cases such as "My order arrived crushed" with no request for a person (`search_knowledge` vs `handoff_to_human`); (4) log tool arguments, e.g. to confirm what Gemini passes to `check_stock` for "croissants". (5) allergen questions about a product can go to either `search_knowledge` or `check_stock` (the products table has an `allergens` column); "Do they contain gluten?" after a croissant stock question picked `search_knowledge`. Decide which tool is "expected" for these.
- **Blocked on:** nothing.
- **Setup notes:** `.env` must exist on each laptop (gitignored; copy from `.env.example` and fill it in). Supabase's Data API must be enabled (Project Settings -> Data API) -- it had been switched off, which caused the earlier `503 PGRST002`. `scripts/verify_setup.py` checks Supabase and Gemini.
- **GitHub remote:** connected -- https://github.com/LizetCh/rag-customer-support-agent
- **Last session:** 2026-11-02 (Mac)

## Session log (most recent first)

### 2026-11-02 (end) -- Historia 4 complete
- The 429s on Render came from the daily quota (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, value 20). The user's API keys for other projects shared one AI Studio project, so this app moved to its own project.
- Confirmed on the public URL by the user: one /chat turn, logged with `search_knowledge` twice, 2320 tokens in, 477 tokens out, $0.003529, 9556 ms.
- README written with real metrics, a flow diagram, design decisions, and limitations.

### 2026-11-02 (later) -- Historia 4 started
- `Dockerfile` and `.dockerignore`: Python 3.12 slim, dependencies installed from the lockfile before the code is copied, non-root user, no secrets in the image, `PORT` from the environment.
- Decision: /chat stays public with no API key and no app-level limit, so recruiters can try it. Gemini's free-tier quota is the cap: `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, value 20, about 10 turns with tools (some calls succeeded after a 429, cause unknown). This is a deliberate, documented exception to "auth by default": tools only read data, the data is fictitious, and the free tier cannot run up a bill. Add auth or a cap before ever enabling billing.
- Decision: keep `InMemorySaver` for the demo. A Postgres checkpointer would store message text in the database, undoing the no-PII decision. List it in the README as a known limitation and the production path.
- Gemini failures now return a generic 503 and are logged. Seen working in the container on a real Gemini 429.
- 13 tests pass.

### 2026-11-02 -- Historia 3 complete
- First full eval run: tool-choice accuracy 20/20, recall@3 20/20. Added recall@1: 19/20.
- `app/telemetry/chat_log.py` sums tokens across a turn's Gemini calls, estimates cost ($0.75 input and $3.75 output per 1M tokens, doubling on 2027-01-01), and writes one `chat_logs` row. A failed insert is logged and the customer still gets a reply.
- Decision: no message text in `chat_logs`, to avoid storing customer PII. The user dropped `user_message` and `agent_response` in Supabase; `supabase/schema.sql` matches.
- Verified: 11 tests pass. The user ran POST /chat live, and `chat_logs` got a row with `search_knowledge`, 1272 tokens in, 212 tokens out, $0.001749, and 7488 ms. Task 2 checked off.

### 2026-10-28 (later) -- Historia 3 started
- `evals/dataset.jsonl`: 20 core questions (12 `search_knowledge` across the 6 docs, 4 `check_stock`, 4 `handoff_to_human`) plus 8 harder retrieval-only paraphrases (`expected_tool: null`, left out of tool scoring to fit the daily quota).
- Allergen rule decided: a question about a specific product's allergens expects `check_stock`; a general allergen policy question expects `search_knowledge`.
- `evals/run_evals.py`: deterministic scoring (no LLM judge). Retrieval calls `search()` directly; tool choice calls the agent node once and reads its first `tool_calls`, without running the full graph. `--retrieval-only` flag skips the chat half.
- Real result: retrieval recall@3 = 20/20 (100%), even on paraphrases. The metric is saturated because there are only 6 documents and 3 slots, so the next step is recall@1.
- Explained: eval sets, recall@k vs MRR, tool-choice accuracy, deterministic eval vs LLM-as-judge, why not evaluate with a different model (DeepSeek/Qwen), and data-jurisdiction concerns. Glossary updated.

### 2026-10-28 -- Historia 2 complete
- Built POST /chat: `app/api/schemas.py` (`ChatRequest`: message 1-2000 chars, optional UUID `session_id`; `ChatResponse`: `session_id`, `reply`, `tools_used`, `escalated`) and `app/api/chat.py` (router wrapping `build_graph()`). The server creates the session id on the first message.
- Conversation memory via LangGraph's `InMemorySaver` checkpointer, keyed by `thread_id` = session id. Lost on restart and not shared across instances, so it must move to a Postgres checkpointer before deploy (Historia 4).
- `tests/test_chat.py`: 3 validation tests (blank, oversized, non-UUID session id -> 422). 6 tests pass.
- Verified in Swagger UI: one question per tool picked the right tool, and a follow-up ("Do they contain gluten?") with the same session id correctly resolved "they" to croissants.

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
