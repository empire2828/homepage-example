import anvil.secrets
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests
from supabase import create_client, Client
from admin import log
from servermain import save_last_fees_as_std
from Users import save_user_apartment_count
from smoobu.smoobu_main import get_price_elements
import requests
from datetime import datetime
from google.cloud import bigquery
from servermain import get_bigquery_client, delete_bookings_by_email
import json
import textwrap

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email'] 
  result= anvil.server.launch_background_task('sync_smoobu',user_email)
  save_smoobu_userid(user_email)
  current_user['server_data_last_update'] = datetime.now()
  return result

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.background_task
def sync_smoobu(user_email):
  client = get_bigquery_client()
  
  delete_bookings_by_email(user_email)
  
  if client is None:
    return "BigQuery-Client konnte nicht erstellt werden. Prüfe Service Account-Konfiguration!"

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
    "from": "2019-01-01",
    "excludeBlocked": True,
    "showCancellation": True,
    "includePriceElements": True,
    "page": 1,
    "limit": 25,   # API-limit: Nicht größer setzen!
  }

  all_bookings = []
  while True:
    resp = requests.get(base_url, headers=headers, params=params)
    if resp.status_code != 200:
      return f"Fehler: {resp.status_code} - {resp.text}"
    data = resp.json()
    bookings = data.get("bookings", [])
    all_bookings.extend(bookings)
    if len(bookings) < params["limit"]:
      break
    params["page"] += 1

  if not all_bookings:
    return "Keine Buchungen gefunden."

    # Daten für BigQuery vorbereiten
  rows_to_insert = []
  for booking in all_bookings:
    price_data = get_price_elements(booking['id'], headers)
    row = {
      "reservation_id": booking.get('id'),
      "id": f"{user_email}_{booking.get('id')}",
      "apartment": booking['apartment']['name'],
      "arrival": booking['arrival'],
      "departure": booking['departure'],
      "created_at": booking.get('created-at', '')[:10] if booking.get('created-at') else None,
      "modified_at": booking.get('modifiedAt', '')[:10] if booking.get('modifiedAt') else None,
      "guestname": booking['guest-name'],
      "channel_name": booking.get('channel', {}).get('name'),
      "guest_email": booking['email'],
      "phone": booking['phone'],
      "adults": booking['adults'] if booking['adults'] is not None else 0,
      "children": booking['children'] if booking['children'] is not None else 0,
      "type": booking['type'],
      "price": float(booking['price']) if booking['price'] is not None else 0,
      "price_paid": booking['price-paid'],
      "prepayment": float(booking['prepayment']) if booking['prepayment'] is not None else 0,
      "prepayment_paid": booking['prepayment-paid'],
      "deposit": float(booking['deposit']) if booking['deposit'] is not None else 0,
      "deposit_paid": booking['deposit-paid'] if booking['deposit-paid'] is not None else "",
      "commission_included": float(booking.get('commission-included') or 0.0),
      "guestid": booking['guestId'],
      "language": booking['language'],
      "email": user_email,
      "supabase_key": supabase_key,
      "price_baseprice": float(price_data.get('price_baseprice', 0)),
      "price_cleaningfee": float(price_data.get('price_cleaningfee', 0)),
      "price_longstaydiscount": float(price_data.get('price_longstaydiscount', 0)),
      "price_coupon": float(price_data.get('price_coupon')) if price_data.get('price_coupon') is not None else 0,
      "price_addon": float(price_data.get('price_addon')) if price_data.get('price_addon') is not None else 0,
      "price_curr": price_data.get('price_curr', ''),
      "price_comm": float(price_data.get('price_comm')) if price_data.get('price_comm') is not None else 0
    }
    rows_to_insert.append(row)

  if not rows_to_insert:
    return "Keine Buchungen zur Übertragung."

  table = "lodginia.lodginia.bookings"
  columns = [
    "reservation_id", "id", "apartment", "arrival", "departure", "created_at",
    "modified_at", "guestname", "channel_name", "guest_email", "phone", "adults",
    "children", "type", "price", "price_paid", "prepayment", "prepayment_paid",
    "deposit", "deposit_paid", "commission_included", "guestid", "language", "email",
    "supabase_key", "price_baseprice", "price_cleaningfee", "price_longstaydiscount",
    "price_coupon", "price_addon", "price_curr", "price_comm"
  ]

  value_rows = []
  for row in rows_to_insert:
    values = []
    for col in columns:
      val = row[col]
      if val is None:
        values.append("NULL")
      elif isinstance(val, (int, float)):
        values.append(str(val))
      else:
        values.append("'" + str(val).replace("'", "''") + "'")
    value_rows.append(f"({', '.join(values)})")

  sql = (f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES\n" +
         ",\n".join(value_rows))
  client.query(sql).result()
  print(f"{len(rows_to_insert)} bookings imported into BigQuery.")

  save_last_fees_as_std(user_email)
  
  return 

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



