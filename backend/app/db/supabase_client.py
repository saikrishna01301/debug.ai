# from supabase import create_client, Client
# from app.core.config import get_settings

# settings = get_settings()

# # Initialize Supabase client
# supabase: Client = create_client(
#     settings.supabase_url,
#     settings.supabase_key
# )

# # For admin operations (use service key)
# supabase_admin: Client = create_client(
#     settings.supabase_url,
#     settings.supabase_service_key
# )


# def get_supabase() -> Client:
#     """Dependency to get Supabase client"""
#     return supabase


# def get_supabase_admin() -> Client:
#     """Dependency to get Supabase admin client"""
#     return supabase_admin
