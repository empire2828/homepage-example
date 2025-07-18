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

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.background_task
def sync_smoobu(user_email):
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
  all_bookings = []
  total_pages = 1
  current_page = 1

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

  bookings_added = 0

  for booking in all_bookings:
    log(str(booking), user_email)
    try:
      reservation_id = booking.get('id')
      channel_name = booking.get('channel', {}).get('name')
      # Use the refactored price extraction function
      price_data = get_price_elements(reservation_id, headers)
      row = {
        "reservation_id": reservation_id,
        "apartment": booking['apartment']['name'],
        "arrival": datetime.strptime(booking['arrival'], "%Y-%m-%d").date().isoformat(),
        "departure": datetime.strptime(booking['departure'], "%Y-%m-%d").date().isoformat(),
        "created_at": datetime.strptime(booking['created-at'], "%Y-%m-%d %H:%M").isoformat(),
        "modified_at": datetime.strptime(booking['modifiedAt'], "%Y-%m-%d %H:%M:%S").isoformat(),
        "guestname": booking['guest-name'],
        "channel_name": channel_name,
        "guest_email": booking['email'],
        "phone": booking['phone'],
        "adults": booking['adults'],
        "children": booking['children'],
        "type": booking['type'],
        "price": booking['price'],
        "price_paid": booking['price-paid'],
        "prepayment": booking['prepayment'],
        "prepayment_paid": booking['prepayment-paid'],
        "deposit": booking['deposit'],
        "deposit_paid": booking['deposit-paid'],
        "commission_included": booking['commission-included'],
        "guestid": booking['guestId'],
        "language": booking['language'],
        "email": user_email,
        "supabase_key": supabase_key,
        "price_baseprice": price_data['price_baseprice'],
        "price_cleaningfee": price_data['price_cleaningfee'],
        "price_longstaydiscount": price_data['price_longstaydiscount'],
        "price_coupon": price_data['price_coupon'],
        "price_addon": price_data['price_addon'],
        "price_curr": price_data['price_curr'],
        "price_comm": price_data['price_comm']
      }
      response = (
        supabase_client
          .from_("bookings")
          .upsert(row, on_conflict="reservation_id,email")
          .execute()
      )
      bookings_added += 1
    except KeyError as e:
      print(f"Missing key in booking data: {e}")
      continue

  anvil.server.launch_background_task('save_user_apartment_count', user_email)
  anvil.server.launch_background_task('save_all_channels_for_user', user_email)

  return f"Erfolgreich {bookings_added} Buchungen mit Adressdaten abgerufen und gespeichert."

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



