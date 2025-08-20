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

def to_sql_value(v, force_string=False):
  """Turn a Python value into a BigQuery literal."""
  import numbers
  from decimal import Decimal

  if v is None:
    return "NULL"
  if isinstance(v, bool):
    return "TRUE" if v else "FALSE"

    # Wenn force_string=True, behandle als String auch wenn numerisch
  if force_string:
    escaped = str(v).replace("'", r"\'")
    return f"'{escaped}'"

  if isinstance(v, numbers.Real) or isinstance(v, Decimal):
    return str(v)

    # String-zu-Zahl-Konvertierung nur wenn nicht explizit als String gewünscht
  if isinstance(v, str):
    try:
      if '.' not in v and 'e' not in v.lower():
        return str(int(v))
      else:
        return str(float(v))
    except (ValueError, TypeError):
      pass

    # Standard String-Behandlung
  escaped = str(v).replace("'", r"\'").replace("\\", "\\\\")
  return f"'{escaped}'"

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
  print('delete_bookings_by_email: gelösche Buchungen',deleted_count,' von ',user_email)

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

@anvil.server.background_task
def save_last_fees_as_std(user_email):
  client = get_bigquery_client()
  # Fetch last booking, including adults and children columns
  query = """
      SELECT 
        price_cleaningfee, 
        price_addon,
        adults,
        children,
        guestname
      FROM `lodginia.lodginia.bookings`
      WHERE email = @user_email
        AND channel_name IN ('Direct booking', 'Website')
        AND arrival < '2099-01-01'
      ORDER BY created_at DESC
      LIMIT 1
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("user_email", "STRING", user_email)]
  )
  query_job = client.query(query, job_config=job_config)
  rows = list(query_job)
  if not rows:
    print('save last fees as std: Keine direkt oder Website Buchungen gefunden ', user_email)
    return 0
  cleaning_fee = rows[0]['price_cleaningfee']
  linen_fee = rows[0]['price_addon']
  adults = rows[0].get('adults', 0)
  children = rows[0].get('children', 0)
  guestname= rows[0].get('guestname', "")
  n_guests = (adults or 0) + (children or 0)
  if n_guests:
    std_linen_fee = float(linen_fee) / n_guests if linen_fee not in ("", None) else None
  else:
    std_linen_fee = None

  # Update existing entry
  update_query = """
        UPDATE `lodginia.lodginia.parameter`
        SET std_cleaning_fee = @std_cleaning_fee,
            std_linen_fee = @std_linen_fee
        WHERE email = @user_email
      """
  update_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("std_cleaning_fee", "FLOAT64", float(cleaning_fee) if cleaning_fee not in ("", None) else None),
      bigquery.ScalarQueryParameter("std_linen_fee", "FLOAT64", std_linen_fee),
      bigquery.ScalarQueryParameter("user_email", "STRING", user_email)
    ]
  )
  result = client.query(update_query, job_config=update_config).result()
  if result.num_dml_affected_rows == 0:
    # Insert new entry if update affected no rows
    insert_query = """
              INSERT INTO `lodginia.lodginia.parameter` (email, std_cleaning_fee, std_linen_fee)
              VALUES (@user_email, @std_cleaning_fee, @std_linen_fee)
            """
    insert_config = bigquery.QueryJobConfig(
      query_parameters=[
        bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
        bigquery.ScalarQueryParameter("std_cleaning_fee", "FLOAT64", float(cleaning_fee) if cleaning_fee not in ("", None) else None),
        bigquery.ScalarQueryParameter("std_linen_fee", "FLOAT64", std_linen_fee),
      ]
    )
    result = client.query(insert_query, job_config=insert_config).result()
  print('save_last_fees_as_std: ', user_email, cleaning_fee, std_linen_fee, guestname)
  return 1


@anvil.server.background_task
def save_all_channels_for_user(user_email):
  client = get_bigquery_client()

  # 1. Fetch all relevant channels for user from bookings
  sql = """
        SELECT channel_name
        FROM `lodginia.lodginia.bookings`
        WHERE email = @user_email
        ORDER BY created_at DESC
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("user_email", "STRING", user_email)]
  )
  bookings = client.query(sql, job_config=job_config).result()
  unique_channels = {row['channel_name'] for row in bookings
                     if row['channel_name'] and row['channel_name'].lower() != "blocked channel"}
  if not unique_channels:
    print("save_all_channels_for_user: Keine Channels für", user_email, "gefunden.")
    return 0

    # 2. Prepare data for batch insert with commission rates from Anvil
  def to_sql_value(val):
    if val is None:
      return "NULL"
    if isinstance(val, str):
      return "'" + val.replace("'", "\\'") + "'"
    return str(val)

  rows = []
  for channel_name in unique_channels:
    row = anvil.tables.app_tables.channels.get(name=channel_name)
    std_commission = row['std_commission_rate'] if row else None
    entry = "({}, {}, {})".format(
      to_sql_value(user_email),
      to_sql_value(channel_name),
      to_sql_value(std_commission)
    )
    rows.append(entry)
  values_sql = ',\n        '.join(rows)

  # 3. DML: First DELETE, then INSERT—all in SQL, no streaming API used!
  #       (Optionally wrap these in a transaction for atomicity.)
  delete_sql = """
        DELETE FROM `lodginia.lodginia.std_commission`
        WHERE email = @user_email
    """
  client.query(delete_sql, job_config=job_config).result()

  insert_sql = f"""
        INSERT INTO `lodginia.lodginia.std_commission` (email, channel_name, channel_commission)
        VALUES
        {values_sql}
    """
  client.query(insert_sql).result()

  print("save_all_channels_for_user: Channels gespeichert:", user_email, list(unique_channels))
  return len(rows)

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
    #print(f"Verbindung zu BigQuery-Projekt erfolgreich: {project_id}")
    return client
  except Exception as e:
    print(f"Fehler beim BigQuery Client Setup: {str(e)}")
    return None




