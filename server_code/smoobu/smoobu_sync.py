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

def sync_smoobu(user_email):
  # Set up credentials/env separately, z.B. via GOOGLE_APPLICATION_CREDENTIALS
  client = get_bigquery_client()
  base_url = "https://login.smoobu.com/api/reservations"
  user = app_tables.users.get(email=user_email)
  if user:
    api_key = user['smoobu_api_key']
    supabase_key = user['supabase_key']
  else:
    return "User not found."

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

  # --- Smoobu Paging ---
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

    # --- Transformiere Buchungsdaten ins BigQuery-Format ---
  row_dicts = []
  for b in all_bookings:
    price_data = get_price_elements(b['id'], headers)
    row_dicts.append({
      "reservation_id": b.get("id"),
      "apartment": b.get("apartment", {}).get("name"),
      "arrival": datetime.strptime(b["arrival"], "%Y-%m-%d").date().isoformat() if b.get("arrival") else None,
      "departure": datetime.strptime(b["departure"], "%Y-%m-%d").date().isoformat() if b.get("departure") else None,
      "created_at": datetime.strptime(b["created-at"], "%Y-%m-%d %H:%M").isoformat() if b.get("created-at") else None,
      "modified_at": datetime.strptime(b["modifiedAt"], "%Y-%m-%d %H:%M:%S").isoformat() if b.get("modifiedAt") else None,
      "guestname": b.get("guest-name"),
      "channel_name": b.get("channel", {}).get("name"),
      "guest_email": b.get("email"),
      "phone": b.get("phone"),
      "adults": b.get("adults"),
      "children": b.get("children"),
      "type": b.get("type"),
      "price": b.get("price"),
      "price_paid": b.get("price-paid"),
      "prepayment": b.get("prepayment"),
      "prepayment_paid": b.get("prepayment-paid"),
      "deposit": b.get("deposit"),
      "deposit_paid": b.get("deposit-paid"),
      "commission_included": b.get("commission-included"),
      "guestid": b.get("guestId"),
      "language": b.get("language"),
      "user_email": user_email,
      "price_baseprice": price_data.get("price_baseprice"),
      "price_cleaningfee": price_data.get("price_cleaningfee"),
      "price_longstaydiscount": price_data.get("price_longstaydiscount"),
      "price_coupon": price_data.get("price_coupon"),
      "price_addon": price_data.get("price_addon"),
      "price_curr": price_data.get("price_curr"),
      "price_comm": price_data.get("price_comm"),
      "ingestion_timestamp": datetime.utcnow().isoformat()
    })

    # --- Einfache Batch-Inserts mit UNNEST ---
  query = """
    INSERT INTO `my_project.bookings.dim_reservation`
    SELECT *
    FROM UNNEST(@bookings)
    """
  # Achte auf die Reihenfolge/Typen der Felder!
  query_params = [
    bigquery.ArrayQueryParameter(
      "bookings",
      "STRUCT<reservation_id STRING, apartment STRING, arrival DATE, departure DATE,"
      "created_at DATETIME, modified_at DATETIME, guestname STRING, channel_name STRING,"
      "guest_email STRING, phone STRING, adults INT64, children INT64, type STRING, price NUMERIC,"
      "price_paid NUMERIC, prepayment NUMERIC, prepayment_paid NUMERIC, deposit NUMERIC,"
      "deposit_paid NUMERIC, commission_included BOOL, guestid STRING, language STRING,"
      "user_email STRING, price_baseprice NUMERIC, price_cleaningfee NUMERIC,"
      "price_longstaydiscount NUMERIC, price_coupon NUMERIC, price_addon NUMERIC,"
      "price_curr STRING, price_comm NUMERIC, ingestion_timestamp TIMESTAMP>",
      [tuple(rd.values()) for rd in row_dicts]
    )
  ]
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



