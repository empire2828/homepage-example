import anvil.server
import anvil.http
from anvil.tables import app_tables
import time
from datetime import datetime, timedelta, timezone
from supabase import create_client
from servermain import get_bigquery_client
from google.cloud import bigquery

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase_client = create_client(supabase_url, supabase_api_key)

@anvil.server.background_task
def delete_old_logs():
  x_days_ago = datetime.now(timezone.utc) - timedelta(days=5)
  # Convert to date only
  x_days_ago_date = x_days_ago.date()

  bq_client = get_bigquery_client()
  query = """
        DELETE FROM `lodginia.lodginia.logs`
        WHERE DATE(created_at) < @older_than
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("older_than", "DATE", x_days_ago_date)
    ]
  )
  job = bq_client.query(query, job_config=job_config)
  job.result()
  print(f"Deleted {job.num_dml_affected_rows} rows.")
  return {
    "deleted_rows": job.num_dml_affected_rows,
    "done": True
  }

