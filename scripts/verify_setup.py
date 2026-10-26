"""One-off sanity check: confirms the Gemini API key and Supabase schema
both work, without ever printing the secrets themselves."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase import create_client

from app.config import settings


def check_supabase() -> None:
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    for table in ("document_chunks", "products", "chat_logs"):
        client.table(table).select("*").limit(1).execute()
        print(f"  table '{table}' exists: OK")

    client.rpc(
        "match_documents",
        {"query_embedding": [0.0] * settings.gemini_embedding_dim, "match_count": 1},
    ).execute()
    print("  match_documents() RPC callable: OK")


def check_gemini() -> None:
    embedder = GoogleGenerativeAIEmbeddings(
        model=f"models/{settings.gemini_embedding_model}",
        google_api_key=settings.google_api_key,
        output_dimensionality=settings.gemini_embedding_dim,
    )
    vector = embedder.embed_query("croissant")
    assert len(vector) == settings.gemini_embedding_dim, (
        f"expected {settings.gemini_embedding_dim} dims, got {len(vector)}"
    )
    print(f"  embedding call OK, got a {len(vector)}-dim vector")


if __name__ == "__main__":
    print("Supabase:")
    check_supabase()
    print("Gemini:")
    check_gemini()
    print("\nAll checks passed.")
