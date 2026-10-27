from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings


@lru_cache
def get_embedder() -> GoogleGenerativeAIEmbeddings:
    # embed_documents() uses task type RETRIEVAL_DOCUMENT and embed_query()
    # uses RETRIEVAL_QUERY, so docs and questions are embedded for search.
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{settings.gemini_embedding_model}",
        google_api_key=settings.google_api_key,
        output_dimensionality=settings.gemini_embedding_dim,
    )
