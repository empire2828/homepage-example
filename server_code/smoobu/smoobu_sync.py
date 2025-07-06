import anvil.secrets
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests
from smoobu.smoobu_main import get_guest_details, guest_data_update
from supabase import create_client, Client
from admin import log

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email'] 
  result= anvil.server.launch_background_task('sync_smoobu',user_email)
  save_smoobu_userid(user_email)
  guest_data_update(user_email)
  current_user['server_data_last_update'] = datetime.now()
  return result

@anvil.server.background_task
def sync_smoobu(user_email):
  base_url = "https://login.smoobu.com/api/reservations"
  user= app_tables.users.get(email=user_email)
  if user:
    api_key= user['smoobu_api_key']
    supabase_key = user['supabase_key']
  else:
    pass

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
      # ACHTUNG: Die API liefert page_count und bookings
      total_pages = data.get("pagination", {}).get("totalPages", 1)
      # oder manchmal page_count
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
    log(str(booking))
    try:
      # Bestehende Buchung anhand der Reservierungs-ID abrufen

      # Gästedaten abrufen
      guest_data = get_guest_details(booking['guestId'], headers)
      address = guest_data.get('address', {})
      city = address.get('city', '')
      postal_code = address.get('postalCode', '')
      country = address.get('country', '')     

      # Preis-Elemente separat abrufen
      reservation_id = booking['id']
      price_baseprice = price_cleaningfee = price_longstaydiscount = price_coupon = price_addon = price_curr = None 
      if reservation_id:
        price_elements_response = requests.get(
          f"https://login.smoobu.com/api/reservations/{reservation_id}/price-elements",
          headers=headers
        )
        if price_elements_response.status_code == 200:
          price_baseprice = None
          price_cleaningfee = None
          price_longstaydiscount = None
          price_coupon = None
          price_addon = None
          price_curr = None
          price_comm= None
          if price_elements_response.status_code == 200:
            price_elements = price_elements_response.json().get("priceElements", [])
            print("reservation id: ",reservation_id, " price_elements: ",price_elements)
            log(price_elements)
            for pe in price_elements:
              if pe.get('type') == 'basePrice':
                price_baseprice = pe.get('amount')
              elif pe.get('type') == 'cleaningFee':
                price_cleaningfee = pe.get('amount')
              elif pe.get('type') == 'longStayDiscount':
                price_longstaydiscount = pe.get('amount')
              elif pe.get('type') == 'addon':
                price_addon = pe.get('amount')
              elif pe.get('type') == 'coupon':
                price_coupon = pe.get('coupon')
              if pe.get('type') == 'commission':
                price_comm = pe.get('amount')
              if pe.get('type') == 'channelCustom' and ( pe.get('name') == 'PASS_THROUGH_RESORT_FEE' or pe.get('name') == 'PASS_THROUGH_LINEN_FEE' ):
                price_addon = price_addon + pe.get('amount')
                #airbnb cleaning fee läuft richtig
              if booking['channel']['name'] == 'booking.com' and pe.get('type') == 'channelCustom':
                price_addon = price_addon + pe.get('amount')
                #booking.com
              price_curr = pe.get('currencyCode')
      row = {
        "reservation_id": booking['id'],
        "apartment": booking['apartment']['name'],
        "arrival": datetime.strptime(booking['arrival'], "%Y-%m-%d").date().isoformat(),
        "departure": datetime.strptime(booking['departure'], "%Y-%m-%d").date().isoformat(),
        "created_at": datetime.strptime(booking['created-at'], "%Y-%m-%d %H:%M").isoformat(),  # Fixed format
        "modified_at": datetime.strptime(booking['modifiedAt'], "%Y-%m-%d %H:%M:%S").isoformat(), 
        "guestname": booking['guest-name'],
        "channel_name": booking['channel']['name'],
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
        "address_postalcode": postal_code,
        "address_city": city,
        "address_country": country,
        "email": user_email,
        "supabase_key": supabase_key,
        "price_baseprice": price_baseprice,
        "price_cleaningfee": price_cleaningfee,  
        "price_longstaydiscount": price_longstaydiscount,
        "price_coupon": price_coupon,
        "price_addon": price_addon,
        "price_curr": price_curr,
        "price_comm": price_comm
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

  anvil.server.launch_background_task('save_user_apartment_count',user_email)

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

@anvil.server.background_task
def save_user_apartment_count(user_email):
    # Step 1: Get distinct apartments for the user from bookings
    rows = app_tables.bookings.search(email=user_email, apartment=q.not_(None))
    unique_apartments = set(row['apartment'] for row in rows)
    count = len(unique_apartments)

    # Step 2: Find the user row in the user table
    user_row = app_tables.users.get(email=user_email)
    if user_row is not None:
        # Step 3: Store the count in the user row (assume column is 'apartment_count')
        user_row['apartment_count'] = count
        print()
        return count
    else:
        # Optionally handle missing user
        raise Exception(f"User with email {user_email} not found")
