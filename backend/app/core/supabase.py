"""
Supabase client configuration
"""
from supabase import create_client, Client
import os
from typing import Optional

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vtisiosocwfnelxumnji.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0aXNpb3NvY3dmbmVseHVtbmppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MDU5MzEsImV4cCI6MjA3ODA4MTkzMX0.oIuRpjQs68D2vfbWiHSnW2zcIDcn2WzUjo0WLoVg3Tg")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0aXNpb3NvY3dmbmVseHVtbmppIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjUwNTkzMSwiZXhwIjoyMDc4MDgxOTMxfQ.8kCayMkv3r7xqEn0e9YVYxLtshKN49IFVbKIYUuiiCE")

# Create Supabase clients
_client: Optional[Client] = None
_admin_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get Supabase client (anon key - respects RLS)"""
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def get_supabase_admin() -> Client:
    """Get Supabase admin client (service key - bypasses RLS)"""
    global _admin_client
    if _admin_client is None:
        _admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _admin_client


# Export for convenience
supabase = get_supabase()
supabase_admin = get_supabase_admin()

