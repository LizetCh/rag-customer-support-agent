-- Run this once in the Supabase SQL editor, after creating the project.
-- Enables pgvector and creates the three tables the agent needs, plus the
-- similarity-search RPC function used by app/rag/search.py.

create extension if not exists vector;

-- Historia 1: knowledge base chunks + their embeddings
create table if not exists document_chunks (
  id bigint generated always as identity primary key,
  source_document text not null,      -- e.g. "faq.md"
  chunk_index int not null,
  content text not null,
  embedding vector(768) not null,
  created_at timestamptz not null default now()
);

create index if not exists document_chunks_embedding_idx
  on document_chunks using hnsw (embedding vector_cosine_ops);

-- RPC used by search_knowledge: cosine similarity top-k search
create or replace function match_documents (
  query_embedding vector(768),
  match_count int default 3
)
returns table (
  id bigint,
  source_document text,
  content text,
  similarity float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.source_document,
    document_chunks.content,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  order by document_chunks.embedding <=> query_embedding
  limit match_count;
$$;

-- Historia 2: fake inventory, queried by the check_stock tool
create table if not exists products (
  id bigint generated always as identity primary key,
  name text not null,
  stock_qty int not null default 0,
  price numeric(10, 2) not null,
  allergens text[] default '{}'
);

-- Historia 3: per-request telemetry logged by /chat
create table if not exists chat_logs (
  id bigint generated always as identity primary key,
  session_id text not null,
  user_message text not null,
  agent_response text not null,
  tool_used text,
  tokens_in int,
  tokens_out int,
  estimated_cost_usd numeric(10, 6),
  latency_ms int,
  escalated boolean not null default false,
  created_at timestamptz not null default now()
);
