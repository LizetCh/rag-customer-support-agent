"""Chunk every docs/*.md file, embed the chunks with Gemini, and store them
in Supabase. Safe to re-run: each doc's old chunks are replaced."""

from pathlib import Path

from app.db.client import get_client
from app.rag.chunking import chunk_markdown
from app.rag.embeddings import get_embedder

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def ingest() -> None:
    client = get_client()
    embedder = get_embedder()

    for path in sorted(DOCS_DIR.glob("*.md")):
        chunks = chunk_markdown(path.read_text(encoding="utf-8"))
        vectors = embedder.embed_documents(chunks)

        rows = [
            {
                "source_document": path.name,
                "chunk_index": i,
                "content": chunk,
                "embedding": vector,
            }
            for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]

        client.table("document_chunks").delete().eq("source_document", path.name).execute()
        client.table("document_chunks").insert(rows).execute()
        print(f"  {path.name}: {len(rows)} chunks")


if __name__ == "__main__":
    print("Ingesting docs/:")
    ingest()
    print("Done.")
