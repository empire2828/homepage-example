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
  x_days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)
  bq_client = get_bigquery_client()
  query = """
        DELETE FROM `lodginia.lodginia.bookings`
        WHERE created_at < @older_than
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("older_than", "TIMESTAMP", x_days_ago)
    ]
  )
  job = bq_client.query(query, job_config=job_config)
  job.result()
  print(f"Deleted {job.num_dml_affected_rows} rows.")
  return {
    "deleted_rows": job.num_dml_affected_rows,
    "done": True
  }

