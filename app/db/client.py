from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache
def get_client() -> Client:
    # Server-side only: the service_role key bypasses RLS.
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
