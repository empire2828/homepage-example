import anvil.email
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import time
from datetime import datetime, timedelta, timezone
from . import routes # noqa: F401
from supabase import create_client, Client
import anvil.secrets
from google.cloud import bigquery
import json
from google.oauth2 import service_account

# BigQuery Konfiguration
PROJECT_ID = "lodginia"
DATASET_ID = "lodginia" 
TABLE_ID = "bookings"
FULL_TABLE_ID = "lodginia.lodginia.bookings"

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def delete_bookings_by_email(user_email):
  client = get_bigquery_client()
  sql = f"""
        DELETE FROM `{FULL_TABLE_ID}`
        WHERE email = @user_email
    """

  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("user_email", "STRING", user_email)
    ]
  )
  query_job = client.query(sql, job_config=job_config)
  query_job.result()  # Wait for the job to finish

  deleted_count = query_job.num_dml_affected_rows
  print('gelösche Buchungen',deleted_count,' von ',user_email)

  return {
    "status": "success",
    "deleted_count": deleted_count,
  }

@anvil.server.callable
def send_registration_notification(user_email):
  anvil.email.send(
    to="dirk.klemer@gmail.com",  # Deine eigene Adresse
    subject="Neuer Benutzer registriert für Lodginia.com",
    text=f"Ein neuer Benutzer hat sich registriert: {user_email}"
  )
    
@anvil.server.callable
def send_email_to_support(text, file=None, email=None):
  attachments = []
  if file is not None:
    attachments.append(file)
  try:
    anvil.email.send(
      to="dirk.klemer@gmail.com",
      subject="Neue Supportanfragen vom Lodginia.com",
      text=text + "\n\n" + str(email),
      attachments=attachments
    )
    print("send_email_to_support: success", email, text)
  except Exception as e:
    print("send_email_to_support: ERROR", e)

def save_last_fees_as_std(user_email):
  client = get_bigquery_client()
  # Suche letzte Buchung des Users für die gewünschten Kanäle
  query = """
      SELECT price_cleaningfee, price_addon
      FROM `lodginia.lodginia.bookings`
      WHERE email = @user_email
        AND channel_name IN ('Direct booking', 'Website')
      ORDER BY created_at DESC
      LIMIT 1
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("user_email", "STRING", user_email)]
  )
  query_job = client.query(query, job_config=job_config)
  rows = list(query_job)
  if not rows:
    return 0
  cleaning_fee = rows[0]['price_cleaningfee']
  addon_fee = rows[0]['price_addon']

  # 2. Versuche Update – überschreibe bestehenden Eintrag
  update_query = """
      UPDATE `lodginia.lodginia.parameter`
      SET std_cleaning_fee = @std_cleaning_fee,
          std_linen_fee = @std_linen_fee
      WHERE email = @user_email
    """
  update_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("std_cleaning_fee", "FLOAT64", float(cleaning_fee) if cleaning_fee not in ("", None) else None),
      bigquery.ScalarQueryParameter("std_linen_fee", "FLOAT64", float(addon_fee) if addon_fee not in ("", None) else None),
      bigquery.ScalarQueryParameter("user_email", "STRING", user_email)
    ]
  )
  result = client.query(update_query, job_config=update_config).result()
  if result.num_dml_affected_rows == 0:
    # 3. Falls kein Update (Row existiert NICHT), dann INSERT
    insert_query = """
          INSERT INTO `your_project.your_dataset.parameter` (email, std_cleaning_fee, std_linen_fee)
          VALUES (@user_email, @std_cleaning_fee, @std_linen_fee)
        """
    insert_config = bigquery.QueryJobConfig(
      query_parameters=[
        bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
        bigquery.ScalarQueryParameter("std_cleaning_fee", "FLOAT64", float(cleaning_fee) if cleaning_fee not in ("", None) else None),
        bigquery.ScalarQueryParameter("std_linen_fee", "FLOAT64", float(addon_fee) if addon_fee not in ("", None) else None),
      ]
    )
    client.query(insert_query, job_config=insert_config).result()
  print('last fees saved as std', user_email, cleaning_fee, addon_fee)
  return 1

@anvil.server.background_task
def save_all_channels_for_user(user_email):
  # 1. Lade alle Buchungen für den Nutzer
  response = (
    supabase_client
      .table("bookings")
      .select("channel_name")
      .eq("email", user_email)
      .order("created_at", desc=True)
      .execute()
  )
  bookings = response.data

  # 2. Extrahiere alle einzigartigen genutzten channel_names
  #    (keine None/Leere, keine 'blocked channel')
  unique_channels = set()
  for booking in bookings:
    channel = booking.get("channel_name")
    # Ignoriere leere Werte UND 'blocked channel'
    if channel and channel.lower() != "Blocked channel":
      unique_channels.add(channel)

    # 3. Für jeden Channel: Hole std_commission_rate aus Anvil Tabelle 'channels'
  upserts = []
  for channel_name in unique_channels:
    row = anvil.tables.app_tables.channels.get(name=channel_name)
    std_commission_rate = row.get('std_commission_rate') if row else None

    upserts.append({
      "email": user_email,
      "channel_name": channel_name,
      "channel_commission": std_commission_rate
    })
    print('std channels added:', channel_name, std_commission_rate)

    # 4. Upsert in std_commission pro Channel
  if upserts:
    supabase_client.table("std_commission").upsert(
      upserts,
      on_conflict="email,channel_name"
    ).execute()
    print("Channels gespeichert:", user_email, list(unique_channels))
    return len(upserts)
  else:
    print("Keine Channels für", user_email, "gefunden.")
    return 0

def get_bigquery_client():
  """Erstellt einen BigQuery Client mit Service Account Authentifizierung"""
  try:
    service_account_json = anvil.secrets.get_secret('bigquery_api_key')
    service_account_info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
      service_account_info,
      scopes=['https://www.googleapis.com/auth/bigquery']
    )
    client = bigquery.Client(
      credentials=credentials,
      project=service_account_info['project_id']
    )
    # Projektname abfragen (Test-Query)
    project_id = service_account_info['project_id']
    client = bigquery.Client(
      credentials=credentials,
      project=project_id
    )
    print(f"Verbindung zu BigQuery-Projekt erfolgreich: {project_id}")
    return client
  except Exception as e:
    print(f"Fehler beim BigQuery Client Setup: {str(e)}")
    return None




