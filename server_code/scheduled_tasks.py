import anvil.server
import anvil.http
from anvil.tables import app_tables
import time
from datetime import datetime, timedelta, timezone
from supabase import create_client

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase_client = create_client(supabase_url, supabase_api_key)

@anvil.server.background_task
def delete_old_logs():
  x_days_ago = datetime.now(timezone.utc) - timedelta(days=5)
  response = (
    supabase_client.table("logs")
      .delete()
      .lt("created_at", x_days_ago.isoformat())
      .execute()
  )
  print(response)
  return {
    "status_code": getattr(response, "status_code", None),
    "data": getattr(response, "data", None),
    "error": getattr(response, "error", None)
  }

