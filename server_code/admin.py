import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media
import csv
from datetime import datetime, timedelta, timezone
import inspect
from supabase import create_client
import os
from google.cloud import bigquery
from servermain import get_bigquery_client
from dateutil.parser import parse
#from userfunctions import get_user_has_subscription_for_email
import time

#supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
#supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
#supabase_client: create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
#supabase_client = create_client(supabase_url, supabase_api_key)

BQ_PROJECT = "lodginia"
BQ_DATASET = "lodginia"
BQ_TABLE   = "logs"

@anvil.server.callable
def log(message: str, email: str = None, function: str = None):
  if email is None:
    user = anvil.users.get_user()
    email = user.get("email") if user and "email" in user else None

  # Convert message to string if it's a complex object
  if not isinstance(message, str):
    message = str(message)

  print(email, message, function)
  
  print(email, message,function)
  
  bq_client = get_bigquery_client()

  query = f"""
        INSERT INTO `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
        (message, email, function)
        VALUES (@msg, @email, @func)
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("msg", "STRING", message),
      bigquery.ScalarQueryParameter("email", "STRING", email),
      bigquery.ScalarQueryParameter("func", "STRING", function)
    ]
  )
  job = bq_client.query(query, job_config=job_config)
  job.result()
  return {"inserted_rows": job.num_dml_affected_rows}

@anvil.server.callable
def search_logs(search_term: str):
  conditions = [
    "LOWER(message) LIKE LOWER(@term_wild)",
    "LOWER(email) LIKE LOWER(@term_wild)"
  ]
  params = [
    bigquery.ScalarQueryParameter("term_wild", "STRING", f"%{search_term}%")
  ]
  if search_term.isdigit():
    conditions.append("CAST(id AS STRING) = @term_exact_int")
    params.append(bigquery.ScalarQueryParameter("term_exact_int", "STRING", search_term))
  try:
    dt = parse(search_term)
    conditions.append("CAST(created_at AS STRING) = @term_exact_ts")
    params.append(bigquery.ScalarQueryParameter("term_exact_ts", "STRING", dt.isoformat()))
  except Exception:
    pass

  where_clause = " OR ".join(conditions)
  query = f"""
        SELECT id, message, email, function, ref_id, created_at
        FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT 1000
    """
  job_config = bigquery.QueryJobConfig(query_parameters=params)
  bq_client = get_bigquery_client()
  job = bq_client.query(query, job_config=job_config)
  rows = job.result()
  results = []
  for row in rows:
    results.append({
      "id":         row["id"],
      "message":    row["message"],
      "email":      row["email"],
      "function":   row["function"],
      "ref_id":     row["ref_id"],
      "created_at": row["created_at"].isoformat()
    })
  return results

@anvil.server.callable
def sync_smoobu_for_all_smoobu_subscribers():
  results = []
  for user in app_tables.users.search():
    # Use the subscription checker function for each user to avoid duplicate logic
    #has_subscription = anvil.server.call('get_user_has_subscription_for_email', user['email'])
    #if has_subscription:
      if not user.get('smoobu_api_key'):
       results.append({'email': user['email'], 'status': 'No API key'})
       continue
      try:
        task = anvil.server.launch_background_task('sync_smoobu', user['email'])
        results.append({'email': user['email'], 'status': 'Task launched', 'task_id': task.task_id})
        time.sleep(60)
      except Exception as e:
        results.append({'email': user['email'], 'status': f'Error: {e}'})
  print (results)
  return results