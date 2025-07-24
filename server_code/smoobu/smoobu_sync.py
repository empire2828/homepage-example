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
from servermain import get_bigquery_client
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
  save_last_fees_as_std(user_email)
  return result

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.background_task
def sync_smoobu(user_email):
  client = get_bigquery_client()
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
    "page": 1,
    "limit": 100,
    "from": "2019-01-01",
    "excludeBlocked": True,
    "showCancellation": True,
    "includePriceElements": True,
  }
  all_bookings = []
  current_page = 1
  total_pages = 1
  while current_page <= total_pages:
    params["page"] = current_page
    resp = requests.get(base_url, headers=headers, params=params)
    if resp.status_code != 200:
      return f"Fehler: {resp.status_code} - {resp.text}"
    data = resp.json()
    total_pages = data.get("pagination", {}).get("totalPages", 1)
    for booking in data.get("bookings", []):
      all_bookings.append(booking)
    current_page += 1
  if not all_bookings:
    return "Keine Buchungen gefunden."
  
  row_dicts = []
  for b in all_bookings:
    price_data = get_price_elements(b['id'], headers)
    reservation_id = booking.get('id')
    channel_name = booking.get('channel', {}).get('name')
    # BigQuery-Typen: Strings, INT, FLOAT, BOOL, DATE, TIMESTAMP 
    rd = {
      "reservation_id": reservation_id,
      "id": user_email+"_"+str(reservation_id),
      "apartment": booking['apartment']['name'],
      "arrival": booking['arrival'],
      "departure": booking['departure'],
      "created_at": booking['created-at'][:10] if booking.get('created-at') else None,
      "modified_at": booking['modifiedAt'][:10] if booking.get('modifiedAt') else None,
      "guestname": booking['guest-name'],
      "channel_name": channel_name,
      "guest_email": booking['email'],
      "phone": booking['phone'],
      "adults": booking['adults'],
      "children": booking['children'],
      "type": booking['type'],
      "price": float(booking['price']),
      "price_paid": booking['price-paid'],
      "prepayment": float(booking['prepayment']),
      "prepayment_paid": booking['prepayment-paid'],
      "deposit": float(booking['deposit']),
      "deposit_paid": booking['deposit-paid'],
      "commission_included": float(booking['commission-included']) if booking['commission-included'] is not None else 0.0,
      "guestid": booking['guestId'],
      "language": booking['language'],
      "email": user_email,
      "supabase_key": supabase_key,
      "price_baseprice": float(price_data['price_baseprice']),
      "price_cleaningfee": float(price_data['price_cleaningfee']),
      "price_longstaydiscount": float(price_data['price_longstaydiscount']),
      "price_coupon": float(price_data['price_coupon']),
      "price_addon": float(price_data['price_addon']),
      "price_curr": price_data['price_curr'],
      "price_comm": float(price_data['price_comm'])
    }
    row_dicts.append(rd)
    
  REQUIRED_FIELDS = [
    "email","apartment","arrival","departure","created_at","channel_name",
    "guestname","adults","children","language","type","reservation_id",
    "guestid","guest_email","phone","price","prepayment","deposit",
    "commission_included","price_paid","prepayment_paid","deposit_paid",
    "id","modified_at","supabase_key",
    "price_baseprice","price_cleaningfee","price_longstaydiscount",
    "price_coupon","price_addon","price_curr","price_comm"
  ]

  for rd in row_dicts:
    for f in REQUIRED_FIELDS:
      rd.setdefault(f, None)

  struct_def = (
    "STRUCT<email STRING, apartment STRING, arrival DATE, departure DATE, created_at DATE,"
    "channel_name STRING, guestname STRING, adults INT64, children INT64, language STRING, type STRING,"
    "reservation_id INT64, guestid INT64, guest_email STRING, phone STRING,"
    "price FLOAT64,"
    "prepayment FLOAT64, deposit FLOAT64, commission_included FLOAT64, price_paid STRING, prepayment_paid STRING,"
    "deposit_paid STRING, id STRING, modified_at DATE,"
    "supabase_key STRING, price_baseprice FLOAT64, price_cleaningfee FLOAT64, price_longstaydiscount FLOAT64,"
    "price_coupon FLOAT64, price_addon FLOAT64, price_curr STRING, price_comm FLOAT64>"
  )

  query = "INSERT INTO `lodginia.lodginia.bookings` SELECT * FROM UNNEST(@bookings)"
  
  # Pass the list of dictionaries directly - no tuple conversion
  query_params = [
    bigquery.ArrayQueryParameter(
      "bookings",
      struct_def,
      row_dicts  # Use dictionaries directly, not tuples
    )
  ]

  #print(json.dumps(row_dicts[0], indent=2, default=str))
  #print(struct_def)
  #print("\n" + "="*60)
  print("STRUCT_DEFINITION:")
  print(textwrap.fill(struct_def, width=100))  # für bessere Lesbarkeit umbrochen
  print("\nSAMPLE ROW_DICT (index 0):")
  print(json.dumps(row_dicts[0], indent=2, default=str))
  print("="*60 + "\n")
  #print(query_params)
  
  job_config = bigquery.QueryJobConfig(query_parameters=query_params)
  client.query(query, job_config=job_config).result()
  
  return f"{len(row_dicts)} Buchungen in BigQuery importiert."

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



