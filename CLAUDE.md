# RAG Customer Support Agent

GitHub repo name: `rag-customer-support-agent` (chosen to be scannable by a hiring manager -- leads with the actual skills demonstrated, RAG + agent + customer support, rather than the bakery flavor text). The local folder on this machine may still be named `bread-agent` for historical reasons; that's cosmetic only and doesn't need to match.

## 1. What this is

A customer-support agent for a fictitious small bakery. It answers customer questions using the bakery's own documents (FAQ, hours, shipping, returns, allergens), checks live inventory, and hands the conversation off to a human when it can't resolve something.

**Why this project:** it's built as a portfolio piece for an AI-engineer job search. It deliberately mirrors the target job's domain — chat-based customer support with human handoff — and demonstrates, end to end, the skills that domain requires: retrieval-augmented generation, a tool-using agent, evaluation of both retrieval and tool choice, cost/latency observability, and a real deploy. Everything uses fictitious data, so it's fully original and stands on its own.

## 2. Tech stack

| Layer | Choice |
|---|---|
| API | FastAPI |
| Agent orchestration | LangGraph |
| LLM (chat + tool calling) | Gemini, `gemini-3.5-flash` |
| Embeddings | Gemini, `gemini-embedding-001`, truncated to 768 dims |
| Vector store + relational data | Supabase (Postgres) with the `pgvector` extension |
| Containerization | Docker |
| Hosting | Render |
| Python tooling | `uv` (pinned to Python 3.12) |

## 3. Architecture

```
Client
  |
  v
POST /chat  (FastAPI)
  |
  v
LangGraph agent node (Gemini, decides what to do)
  |
  +--> search_knowledge  -> pgvector similarity search (Supabase RPC match_documents) -> top-3 chunks + source
  +--> check_stock       -> SQL lookup on the products table (name, stock_qty, price, allergens)
  +--> handoff_to_human  -> flags the session as escalated (no LLM answer needed after this)
  |
  v
Gemini generates the final reply using whatever the tool returned
  |
  v
Response returned to client, and the turn is logged to chat_logs
  (session id, tokens in/out, estimated cost, latency, tool used)
```

## 4. Repository layout

```
bread-agent/
|-- CLAUDE.md          # this file -- project brief, roadmap, working agreement
|-- PROGRESS.md        # live session-tracking file -- read this first every session
|-- README.md          # human-facing readme: setup steps, architecture diagram, eval results
|-- GLOSSARY.md        # plain-language definitions of terms introduced as we build
|-- pyproject.toml     # uv-managed deps
|-- .env.example       # required env vars, no real secrets
|-- supabase/
|   `-- schema.sql       # document_chunks (pgvector), products, chat_logs tables + match_documents RPC
|-- docs/              # the bakery's own source documents (FAQ, hours, shipping...) -- Historia 1
|-- scripts/           # one-off CLI scripts: ingestion, product seeding -- Historia 1
|-- evals/             # eval dataset + retrieval/tool-choice scoring scripts -- Historia 3
|-- app/
|   |-- main.py          # FastAPI app, currently just GET /health
|   |-- config.py        # settings loaded from env vars (pydantic-settings)
|   |-- db/              # Supabase client + queries
|   |-- rag/             # chunking, embedding, top-k search -- Historia 1
|   |-- agent/           # LangGraph graph + tool definitions -- Historia 2
|   |-- api/             # /chat request/response schemas + router -- Historia 2
|   `-- telemetry/       # token/cost/latency logging -- Historia 3
`-- tests/
    `-- test_health.py    # proves the app boots and pytest works
```

## 5. Roadmap (Definition of Done per item)

Check an item only after the user has confirmed, by actually running it, that it works, not just because the code was written. For the current exact step, see PROGRESS.md, it is more precise than this checklist.

- [x] **Setup**: CLAUDE.md, repo scaffold, uv-managed Python 3.12 env, /health endpoint, GitHub remote connected. DoD: `uv run pytest` passes, `uv run uvicorn app.main:app --reload` boots, repo pushed to GitHub.

**Historia 1 -- Knowledge base & RAG (~4h)**
- [x] Write 5-8 short bakery documents: FAQ, hours, shipping, returns, allergens. DoD: .md files committed under docs/.
- [x] Ingestion script: chunk the docs, embed each chunk with Gemini, store in Supabase/pgvector. DoD: chunks exist in Supabase with their embedding and source-document metadata.
- [x] Top-k search function. DoD: given a question, returns the 3 most relevant chunks with their source document.

**Historia 2 -- Agent with tools (~4h)**
- [x] LangGraph graph with three tools: search_knowledge, check_stock, handoff_to_human. DoD: on 3 test questions (one per tool), the agent picks the right tool each time.
- [x] POST /chat endpoint with Pydantic schemas and a session id. DoD: works end-to-end from the Swagger UI.

**Historia 3 -- Evaluation & cost (~2.5h)**
- [ ] 20-question eval set, each with an expected source document and an expected tool; a script scoring retrieval recall@3 and tool-choice accuracy. DoD: the script prints both metrics.
- [ ] Log tokens, estimated cost, and latency per request. DoD: every /chat response is persisted with that data.

**Historia 4 -- Deploy (~1.5h)**
- [ ] Dockerfile, deploy on Render, README with a flow diagram and real eval numbers. DoD: public URL, README shows real metrics (not placeholders).

**Historia 5 -- "What the RAG?" visualizer (optional, only after Historia 4 is deployed)**
- [ ] A page that shows, for one question: a 2D projection (PCA or UMAP) of all chunk embeddings colored by source document, the question's point with lines to its top-3 chunks (hover shows chunk text and similarity), the agent's path through the graph node by node (via `graph.stream`), and the turn's tokens, cost, and latency. Must state that the 2D map distorts distances and the real ranking is cosine similarity in 768 dims. DoD: works on the public deploy for any question.

## 6. Working agreement (how Claude should operate in this repo)

This repo exists so the user, a complete newbie, ends up able to explain and defend every part of it in a job interview. That changes how work happens here, compared to a normal "just ship the code" repo:

- **Claude writes the implementation.** The user isn't expected to type the code themselves in this project.
- **Explain before implementing.** Before writing code for a new concept (chunking, embeddings, tool calling, a LangGraph state graph, recall@k, etc.), give a short plain-language explanation of what it is and why it's the right tool here, *then* write the code.
- **Check understanding before moving on.** After each meaningful chunk of work, ask the user 1-2 comprehension-check questions. Wait for their answer. If they're off, correct gently and re-explain rather than steamrolling ahead.
- **Tie decisions to the portfolio story.** Call out, explicitly, how a given choice would be explained to an interviewer (e.g. "why pgvector over a dedicated vector DB," "why recall@3 and not just accuracy").
- **Keep GLOSSARY.md current.** Whenever a new piece of jargon is introduced, add a one-paragraph plain-language entry.
- **Everything in English** -- code, comments, commit messages, docs, and the bakery's own fictitious content.
- **Don't check off a roadmap item** in Section 5 until the user has confirmed the corresponding DoD actually passes.
- **One Historia at a time.** Don't jump ahead to later Historias' code before earlier ones are checked off, even if it would be convenient.

## 7. Environment & secrets

Defined in .env.example, copied locally to .env (gitignored, never shown to or requested by Claude):

| Var | Purpose |
|---|---|
| GOOGLE_API_KEY | Gemini API key (Google AI Studio) -- chat + embeddings |
| GEMINI_CHAT_MODEL | defaults to gemini-3.5-flash |
| GEMINI_EMBEDDING_MODEL | defaults to gemini-embedding-001 |
| GEMINI_EMBEDDING_DIM | defaults to 768 |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_SERVICE_ROLE_KEY | Supabase service-role key (server-side only, never exposed to a client) |
| APP_ENV | development / production |

## 8. Commands

```bash
uv sync                               # install/sync dependencies
uv run uvicorn app.main:app --reload  # run the API locally
uv run pytest -q                      # run tests
```

Docker/Render steps are added in Historia 4, once there's an actual API worth deploying.

## 9. Git / GitHub status

Local repo only for now. Once the user creates the GitHub remote and shares the URL, connect with:

```bash
git remote add origin <url>
git push -u origin main
```

## 10. Session start/end protocol

The user works across multiple laptops/sessions and relies on this repo (not chat memory) to resume correctly. This is a standing, pre-authorized instruction, do it automatically, no need to re-ask each time:

- **Start of session:** run `git pull` (if a remote is connected), then read PROGRESS.md before doing anything else, and tell the user in one short line where things stand (current Historia/task, next concrete step).
- **End of session:** whenever the user signals they're stopping (e.g. "I'm tired," "let's stop here," "I'm done for today," "I have to go," or similar), before ending:
  1. Update PROGRESS.md's "Current status" block with what was just finished and the precise next step.
  2. `git add -A && git commit` with a short, accurate message.
  3. `git push` if a remote is connected. If not, say so explicitly instead of silently skipping it.
  4. State out loud that this happened, this should never be a silent background action.
