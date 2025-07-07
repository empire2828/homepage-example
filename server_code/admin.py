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

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase_client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def import_bookings_csv(csv_file):
  imported_count = 0

  # 1. Hole die Spaltennamen und Typen aus der Tabelle
  column_info = {c['name']: c['type'] for c in app_tables.bookings.list_columns()}  # z.B. {'email': 'string', ...}

  with anvil.media.TempFile(csv_file) as file_name:
    with open(file_name, 'r', encoding='utf-8-sig') as f:
      reader = csv.DictReader(f, quoting=csv.QUOTE_MINIMAL)
      for row in reader:
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
          app_tables.bookings.add_row(**processed_row)
          imported_count += 1

  return f"{imported_count} Zeilen erfolgreich importiert"

@anvil.server.callable
def log(message: str):
  # Aktuelle Benutzerinformationen abrufen
  user = anvil.users.get_user()
  if user is not None:
    email = user['email']
  else:
    email = None
  # Name der aufrufenden Funktion ermitteln
  caller_function = inspect.stack()[1].function

  # Log-Eintrag vorbereiten
  log_entry = {
    'message': message,
    'email': email,
    'function': caller_function
  }

  # Log-Eintrag in die Tabelle 'logs' schreiben
  response = supabase_client.table('logs').insert(log_entry).execute()
  return response

@anvil.server.callable
def delete_old_logs():
  # Zeitstempel für "vor 3 Tagen"
  three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
  # Lösche alle Zeilen mit created_at < three_days_ago
  response = (
    supabase_client.table("logs")
      .delete()
      .lt("created_at", three_days_ago.isoformat())
      .execute()
  )
  return response

@anvil.server.callable
def search_logs(search_term: str):
  response = (
    supabase_client.table("logs")
      .select("*")
      .ilike("message", f"%{search_term}%")
      .order("created_at", desc=True)
      .execute()
  )
  # Fehlerbehandlung über status_code
  if hasattr(response, 'status_code') and response.status_code != 200:
    return []
    # Optional: Prüfung, ob Daten vorhanden sind
  if not getattr(response, 'data', None):
    return []
  return response.data