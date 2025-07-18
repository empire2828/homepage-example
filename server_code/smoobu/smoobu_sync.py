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
from smoobu.main import fetch_and_store_price_elements, 

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

@anvil.server.background_task
def smoobu_sync(user_email):
  base_url = "https://login.smoobu.com/api/reservations"
  try:
    api_key, supabase_key = get_user_api_keys(user_email)
  except Exception as e:
    print(str(e))
    return

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

  # Alle Buchungen abrufen; ggf. Seitenweise
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
        print("Fehler: Unerwartete API-Antwort")
        return
      current_page += 1
    else:
      print(f"Fehler: {response.status_code} - {response.text}")
      return

  bookings_added = 0
  for booking in all_bookings:
    try:
      channel_name = booking.get("channel", {}).get("name")
      if channel_name == "Blocked channel":
        continue  # Überspringen

      price_elements = booking.get("priceElements", [])
      price_data = fetch_and_store_price_elements(price_elements, )
      # Daten-Objekt für Supabase-Insert/Update
      row = {
        "reservation_id": booking.get("id"),
        "apartment": booking.get("apartment", {}).get("name"),
        "arrival": booking.get("arrival"),
        "departure": booking.get("departure"),
        "created_at": booking.get("created-at"),
        "modified_at": booking.get("modifiedAt"),
        "guestname": booking.get("guest-name"),
        "channel_name": channel_name,
        "guest_email": booking.get("email"),
        "phone": booking.get("phone"),
        "adults": booking.get("adults"),
        "children": booking.get("children"),
        "type": booking.get("type"),
        "price": booking.get("price"),
        "price_paid": booking.get("price-paid"),
        "prepayment": booking.get("prepayment"),
        "prepayment_paid": booking.get("prepayment-paid"),
        "deposit": booking.get("deposit"),
        "deposit_paid": booking.get("deposit-paid"),
        "commission_included": booking.get("commission-included"),
        "guestid": booking.get("guestId"),
        "language": booking.get("language"),
        "email": user_email,
        "supabase_key": supabase_key,
        **price_data
      }
      upsert_booking(row)
      bookings_added += 1
    except Exception as e:
      print(f"Fehler bei Buchung {booking.get('id')}: {str(e)}")
      continue

  anvil.server.launch_background_task('save_user_apartment_count', user_email)
  anvil.server.launch_background_task('save_all_channels_for_user', user_email)
  print(f"Erfolgreich {bookings_added} Buchungen synchronisiert.")

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



