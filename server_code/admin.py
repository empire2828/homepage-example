import anvil.email
import anvil.secrets
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
from google.oauth2 import service_account
import json
from servermain import get_bigquery_client

# BigQuery Konfiguration
BIGQUERY_PROJECT_ID = "lodginia"
BIGQUERY_DATASET_ID = "lodginia" 
BIGQUERY_TABLE_ID = "bookings"
FULL_TABLE_ID = "lodginia.lodginia.bookings"

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase_client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def import_csv(csv_file):
  imported_count = 0

  # 1. Hole die Spaltennamen und Typen aus der Tabelle
  column_info = {c['name']: c['type'] for c in app_tables.channels.list_columns()}  # z.B. {'email': 'string', ...}

  with anvil.media.TempFile(csv_file) as file_name:
    with open(file_name, 'r', encoding='latin-1') as f:
      reader = csv.DictReader(f, delimiter=';')
      for row in reader:
        print(row)
        processed_row = {}
        for col_name, value in row.items():
          clean_col_name = col_name.strip('"').strip()
          # Nur Spalten importieren, die es in der Tabelle gibt (und nicht ID)
          if clean_col_name == "ID" or clean_col_name not in column_info:
            continue
          if not value or not str(value).strip():
            continue  # Leere Werte überspringen
          clean_value = str(value).strip('"').strip()
          col_type = column_info[clean_col_name]
          try:
            # Typkonvertierung je nach Spaltentyp
            if col_type == 'date':
              for date_format in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                try:
                  processed_row[clean_col_name] = datetime.strptime(clean_value, date_format).date()
                  break
                except ValueError:
                  continue
              else:
                continue  # Kein gültiges Datumsformat, Spalte überspringen
            elif col_type == 'datetime':
              for datetime_format in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S', '%Y-%m-%d']:
                try:
                  if len(clean_value) == 10:
                    processed_row[clean_col_name] = datetime.strptime(clean_value, '%Y-%m-%d')
                  else:
                    processed_row[clean_col_name] = datetime.strptime(clean_value, datetime_format)
                  break
                except ValueError:
                  continue
              else:
                continue  # Kein gültiges Datetime-Format, Spalte überspringen
            elif col_type == 'number':
              clean_value = clean_value.replace(',', '.')
              try:
                processed_row[clean_col_name] = float(clean_value) if '.' in clean_value else int(clean_value)
              except Exception:
                continue  # Fehlerhafte Zahl, Spalte überspringen
            elif col_type == 'bool':
              processed_row[clean_col_name] = clean_value.lower() in ['true', '1', 'yes', 'ja', 'wahr']
            else:
              processed_row[clean_col_name] = clean_value
          except Exception:
            continue  # Fehlerhafte Spalte überspringen
        if processed_row:
          app_tables.channels.add_row(**processed_row)
          imported_count += 1

  return f"{imported_count} Zeilen erfolgreich importiert"

@anvil.server.callable
def log(message: str, email: str = None , ref_id: str = None):

  # Nur wenn keine E-Mail übergeben wurde, selbst nachschauen
  if email is None:
    user = anvil.users.get_user()
    print('user', user)
    if user is not None and 'email' in user:
      email = user['email']
    else:
      email = None

    # Name der aufrufenden Funktion ermitteln
  caller_function = inspect.stack()[1].function

  # Log-Eintrag vorbereiten
  log_entry = {
    'message': message,
    'email': email,
    'function': caller_function,
    'ref_id': ref_id
  }

  # Log-Eintrag in die Tabelle 'logs' schreiben
  response = supabase_client.table('logs').insert(log_entry).execute()
  return response
pass

@anvil.server.callable
def search_logs(search_term: str):
  filters = [
    f"message.ilike.%{search_term}%",
    f"email.ilike.%{search_term}%"
  ]
  # Suche nach exakter ID, falls numerisch
  if search_term.isdigit():
    filters.append(f"id.eq.{int(search_term)}")
    # Suche nach exaktem Zeitstempel, falls das Suchwort ISO-Format hat
  from dateutil.parser import parse
  try:
    # Prüft, ob Suchbegriff als Datum interpretierbar ist
    parsed_date = parse(search_term)
    filters.append(f"created_at.eq.{parsed_date.isoformat()}")
  except Exception:
    pass

  or_condition = ",".join(filters)
  response = (
    supabase_client
      .table("logs")
      .select("*")
      .or_(or_condition)
      .order("created_at", desc=True)
      .execute()
  )
  if hasattr(response, 'status_code') and response.status_code != 200:
    return []
  if not getattr(response, 'data', None):
    return []
  return response.data

# BigQuery Configuration
FULL_TABLE_ID = "lodginia.lodginia.bookings"

@anvil.server.background_task
def cleanup_deleted_bookings():
  """
    Overnight cleanup task to permanently delete rows where is_deleted = TRUE
    This runs when streaming buffer has cleared (avoiding the 90-minute restriction)
    """
  print(f"Starting cleanup task at {datetime.now()}")

  try:
    # Initialize BigQuery client
    bq_client = get_bigquery_client()
    if not bq_client:
      print("Error: BigQuery Client could not be created")
      return {"status": "error", "message": "BigQuery client initialization failed"}

      # Check if table has streaming buffer (optional safety check)
    table_ref = bq_client.get_table(FULL_TABLE_ID)
    if hasattr(table_ref, 'streaming_buffer') and table_ref.streaming_buffer:
      print("Warning: Table still has streaming buffer - cleanup may fail")

      # Count rows to be deleted (for logging)
    count_query = f"""
            SELECT COUNT(*) as deleted_count
            FROM `{FULL_TABLE_ID}`
            WHERE is_deleted = TRUE
        """

    count_result = list(bq_client.query(count_query).result())
    rows_to_delete = count_result[0].deleted_count if count_result else 0

    print(f"Found {rows_to_delete} rows marked for deletion")

    if rows_to_delete == 0:
      return {"status": "success", "message": "No rows to delete", "deleted_count": 0}

      # Execute the DELETE statement
    delete_query = f"""
            DELETE FROM `{FULL_TABLE_ID}`
            WHERE is_deleted = TRUE
        """

    # Run the delete job
    delete_job = bq_client.query(delete_query)
    delete_job.result()  # Wait for completion

    # Log results
    rows_affected = delete_job.num_dml_affected_rows
    print(f"Cleanup completed successfully. Deleted {rows_affected} rows")

    return {
      "status": "success", 
      "message": f"Successfully deleted {rows_affected} rows",
      "deleted_count": rows_affected,
      "completed_at": datetime.now().isoformat()
    }

  except Exception as e:
    error_msg = f"Cleanup task failed: {str(e)}"
    print(error_msg)
    return {"status": "error", "message": error_msg}

# Optional: Manual trigger function for testing
@anvil.server.callable
def trigger_manual_cleanup():
    # Launch the cleanup task
  task = anvil.server.launch_background_task('cleanup_deleted_bookings')

  return {
    "status": "launched", 
    "task_id": task.get_id(),
    "message": "Cleanup task launched successfully"
  }

