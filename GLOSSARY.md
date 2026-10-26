# Glossary

Plain-language definitions of terms as they come up while building this project. Add a new entry whenever a new piece of jargon is introduced -- this is meant to double as interview prep.

**LLM (Large Language Model)** -- a model trained on huge amounts of text that predicts the next chunk of text given some input. Here, Gemini is the LLM: it both generates the chat replies and decides which tool to call.

**Embedding** -- a list of numbers (a vector) that represents the meaning of a piece of text, produced by a model. Texts with similar meaning end up with vectors that are close together, which is what makes similarity search possible.

**Vector database** -- a database built (or extended) to store embeddings and search them by similarity instead of by exact match. We're using Postgres with the pgvector extension via Supabase, rather than a dedicated vector-only database, since it also holds our regular relational tables (products, logs).

**RAG (Retrieval-Augmented Generation)** -- instead of asking the LLM to answer purely from what it memorized during training, you first retrieve the most relevant pieces of your own documents, then hand them to the LLM as context so it answers grounded in your actual data.

**Agent** -- an LLM that isn't just generating text, but can decide, step by step, to call tools (functions) to gather information or take actions, then use the results to keep reasoning or produce a final answer.

**Tool calling (function calling)** -- a feature of modern LLMs where the model can choose to invoke one of a set of functions you've described to it (with a name, a description, and arguments), instead of only producing free text.

**Token** -- the unit LLMs actually process text in (roughly a word or part of a word). API usage and cost are billed per token, which is why we log tokens in and out per request.

**Latency** -- how long a request takes end to end, typically measured in milliseconds. Important to log per request so we can reason about and report real performance, not guesses.

**recall@k** -- a retrieval metric: out of all the questions in an eval set, what fraction had their correct source document show up somewhere in the top k search results. We use recall@3 since the agent's search_knowledge tool returns the top 3 chunks.
