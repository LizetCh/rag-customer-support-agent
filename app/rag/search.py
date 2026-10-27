"""Top-k similarity search over document_chunks."""

import sys

from app.db.client import get_client
from app.rag.embeddings import get_embedder


def search(question: str, k: int = 3) -> list[dict]:
    """Return the k chunks closest in meaning to the question.

    Each result has source_document, content, and similarity (cosine, higher
    is closer). Results are never empty: the closest chunks come back even if
    none of them is actually relevant.
    """
    vector = get_embedder().embed_query(question)
    response = get_client().rpc(
        "match_documents", {"query_embedding": vector, "match_count": k}
    ).execute()
    return response.data


if __name__ == "__main__":
    for result in search(" ".join(sys.argv[1:])):
        print(f"[{result['similarity']:.3f}] {result['source_document']}")
        print(f"  {result['content'].splitlines()[0]}\n")
