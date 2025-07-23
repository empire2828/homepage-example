import anvil.secrets
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests
import json
import os
import tempfile
from google.cloud import bigquery
from google.oauth2 import service_account
from admin import log
from servermain import save_last_fees_as_std
from Users import save_user_apartment_count
from smoobu.smoobu_main import get_price_elements, get_bigquery_client
from google.cloud.bigquery_storage_v1 import BigQueryWriteClient, types, writer

import time
import sys
import csv
from google.cloud import storage

import pandas as pd
import pyarrow as pa

# BigQuery Konfiguration
PROJECT_ID = "lodginia"
DATASET_ID = "lodginia" 
TABLE_ID = "bookings"
FULL_TABLE_ID = "lodginia.lodginia.bookings"
TABLE_PATH = "lodginia.lodginia.bookings"

service_account_json = anvil.secrets.get_secret('bigquery_api_key')
with open('/tmp/bq_key.json', 'w') as f:
  f.write(service_account_json)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/bq_key.json'
stream_name = f"projects/{PROJECT_ID}/datasets/{DATASET_ID}/tables/{TABLE_ID}/streams/_default"

@anvil.server.callable
def save_smoobu_userid(user_email):
    smoobu_userid = str(get_smoobu_userid(user_email))
    current_user = anvil.users.get_user()
    app_tables.users.get(email=current_user['email']).update(smoobu_userid=smoobu_userid)
    return 

@anvil.server.callable
def get_smoobu_userid(user_email):
    user = app_tables.users.get(email=user_email)
    if not user:
        print(f"Kein Benutzer mit der E-Mail {user_email} gefunden")
        return None        
    api_key = user['smoobu_api_key']
    if not api_key:
        print(f"Kein API-Key für Benutzer {user_email} gefunden")
        return None    
    headers = {
        "Api-Key": api_key,
        "Cache-Control": "no-cache"
    }    
    try:
        response = requests.get("https://login.smoobu.com/api/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("get_smoobu_userid: ", data['id'])
            return data['id']
        else:
            print(f"API request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Fehler bei der API-Anfrage: {str(e)}")
        return None

################################################################################
# Zusätzliche Imports oben in server_module.py hinzufügen
# Konfiguration (anpassen an dein Setup)

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email']
  result = anvil.server.launch_background_task('sync_smoobu', user_email)
  save_smoobu_userid(user_email)
  current_user['server_data_last_update'] = datetime.now()
  save_last_fees_as_std(user_email)
  return result

@anvil.server.background_task
def sync_smoobu(user_email):
  import requests

  print('starte sync_smoobu')
  base_url = "https://login.smoobu.com/api/reservations"
  user = app_tables.users.get(email=user_email)
  if not user:
    return "User not found."

  api_key = user['smoobu_api_key']
  supabase_key = user['supabase_key']

  headers = {
    "Api-Key": api_key,
    "Content-Type": "application/json"
  }
  params = {
    "status": "confirmed",
    "page": 1,
    "limit": 100,
    "from": "2019-01-01",
    "excludeBlocked": True,
    "showCancellation": True,
    "includePriceElements": True,
  }

  all_bookings = []
  total_pages = 1
  current_page = 1

  # --- Buchungsdaten von Smoobu API abrufen ---
  while current_page <= total_pages:
    params["page"] = current_page
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
      data = response.json()
      total_pages = data.get("pagination", {}).get("totalPages", 1)
      if "page_count" in data:
        total_pages = data["page_count"]
      if "bookings" in data:
        all_bookings.extend(data["bookings"])
      else:
        return "Error: Unexpected API response structure"
      current_page += 1
    else:
      return f"Fehler: {response.status_code} - {response.text}"

    # --- Buchungsdaten für BigQuery vorbereiten ---
  rows_for_bigquery = []
  for booking in all_bookings:
    try:
      reservation_id = booking.get('id')
      channel_name = booking.get('channel', {}).get('name')
      price_data = get_price_elements(reservation_id, headers)  # <- Diese Funktion muss vorhanden sein

      row = {
        "reservation_id": str(reservation_id),
        "apartment": booking['apartment']['name'],
        "arrival": datetime.strptime(booking['arrival'], "%Y-%m-%d").date().isoformat(),
        "departure": datetime.strptime(booking['departure'], "%Y-%m-%d").date().isoformat(),
        "created_at": booking['created-at'][:10],
        "modified_at": booking['modifiedAt'][:10],
        "guestname": booking['guest-name'],
        "channel_name": channel_name if channel_name else '',
        "guest_email": booking['email'] if booking['email'] else '',
        "phone": booking['phone'] if booking['phone'] else '',
        "adults": booking['adults'] if booking['adults'] else 0,
        "children": booking['children'] if booking['children'] else 0,
        "type": booking['type'] if booking['type'] else '',
        "price": float(booking['price']) if booking['price'] else 0.0,
        "price_paid": booking['price-paid'] if booking['price-paid'] else '',
        "prepayment": float(booking['prepayment']) if booking['prepayment'] else 0.0,
        "prepayment_paid": booking['prepayment-paid'] if booking['prepayment-paid'] else '',
        "deposit": float(booking['deposit']) if booking['deposit'] else 0.0,
        "deposit_paid": booking['deposit-paid'] if booking['deposit-paid'] else '',
        "commission_included": float(booking['commission-included']) if booking['commission-included'] else 0,
        "guestid": int(booking['guestId']) if booking.get('guestId') else 0,
        "language": booking['language'] if booking['language'] else '',
        "email": user_email if user_email else '',
        "supabase_key": supabase_key,
        "price_baseprice": float(price_data['price_baseprice']) if price_data['price_baseprice'] else 0.0,
        "price_cleaningfee": float(price_data['price_cleaningfee']) if price_data['price_cleaningfee'] else 0.0,
        "price_longstaydiscount": float(price_data['price_longstaydiscount']) if price_data['price_longstaydiscount'] else 0.0,
        "price_coupon": float(price_data['price_coupon']) if price_data['price_coupon'] else 0.0,
        "price_addon": float(price_data['price_addon']) if price_data['price_addon'] else 0.0,
        "price_curr": price_data['price_curr'] if price_data['price_curr'] else '',
        "price_comm": float(price_data['price_comm']) if price_data['price_comm'] else 0.0,
        "id": f"{user_email}_{reservation_id}"
      }
      rows_for_bigquery.append(row)
    except Exception as e:
      print(f"Fehler beim Verarbeiten der Buchung {reservation_id}: {str(e)}")
      continue

  if not rows_for_bigquery:
    return "Keine Buchungen zu verarbeiten"

  print('1. row:', rows_for_bigquery[0])
  print('Anzahl rows:', len(rows_for_bigquery))

  # --- Storage Write API: Arrow-Schema aus BQ-Tabelle ableiten ---
  try:
    bq_client = bigquery.Client()
    table = bq_client.get_table(TABLE_PATH)

    # Arrow-Schema erstellen
    arrow_schema = pa.schema([
      pa.field(f.name, pa.string()) if f.field_type == "STRING" else
      pa.field(f.name, pa.float64()) if f.field_type == "FLOAT" else
      pa.field(f.name, pa.int64()) if f.field_type in ("INTEGER", "INT64") else
      pa.field(f.name, pa.string())
      for f in table.schema
    ])

    # Stream Name definieren - WICHTIG: Das ist der fehlende Teil!
    stream_name = f"{TABLE_PATH}/streams/_default"

    # Schema serialisieren - WICHTIG: Das ist der andere fehlende Teil!
    serialized_schema = arrow_schema.serialize().to_pybytes()

    # BigQuery Write Client initialisieren
    write_client = BigQueryWriteClient()

    # Stream mit Arrow-Schema öffnen
    stream = writer.AppendRowsStream(
      write_client,
      types.AppendRowsRequest(
        write_stream=stream_name,
        arrow_schema=types.ArrowSchema(serialized_schema=serialized_schema)
      )
    )

    # Daten zu Arrow-Format konvertieren
    df = pd.DataFrame(rows_for_bigquery)
    batch = pa.Table.from_pandas(df, schema=arrow_schema).combine_chunks()
    record_batch = pa.ipc.write_ipc_stream(batch).to_pybytes()

    # Request erstellen und senden
    request = types.AppendRowsRequest()
    request.arrow_record_batch.serialized_record_batch = record_batch
    future = stream.send(request)
    future.result()
    stream.close()

    print(f"Erfolgreich {len(rows_for_bigquery)} Buchungen via Storage Write API eingefügt")

  except Exception as e:
    print(f"Storage Write API Fehler: {str(e)}")
    return f"Storage Write API Fehler: {str(e)}"

    # Background Tasks starten
  anvil.server.launch_background_task('save_user_apartment_count', user_email)
  anvil.server.launch_background_task('save_all_channels_for_user', user_email)

  return f"Erfolgreich {len(rows_for_bigquery)} Buchungen via Storage Write API gespeichert."