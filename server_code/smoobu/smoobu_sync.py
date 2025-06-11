#import anvil.email
#import anvil.secrets
import anvil.users
#import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests
from smoobu.smoobu_main import get_guest_details, guest_data_update

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
  else:
    pass

  headers = {
    "Api-Key": api_key,
    "Content-Type": "application/json"
  }

  params = {
    "status": "confirmed",
    "page": 1,
    "limit": 100
  }
  #"start_date": datetime.now().strftime("%Y-%m-%d"),

  all_bookings = []
  total_pages = 1
  current_page = 1

  while current_page <= total_pages:
    params["page"] = current_page
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
      data = response.json()

      if "pagination" in data and "totalPages" in data["pagination"]:
        total_pages = data["pagination"]["totalPages"]

      if "bookings" in data:
        all_bookings.extend(data["bookings"])
      else:
        return "Error: Unexpected API response structure"

      current_page += 1
    else:
      return f"Fehler: {response.status_code} - {response.text}"

  bookings_added = 0
  for booking in all_bookings:
    try:
      # Bestehende Buchung anhand der Reservierungs-ID abrufen
      existing = app_tables.bookings.get(reservation_id=booking['id'], email=user_email)

      # Gästedaten abrufen
      guest_data = get_guest_details(booking['guestId'], headers)
      address = guest_data.get('address', {})
      street = address.get('street', '')
      city = address.get('city', '')
      postal_code = address.get('postalCode', '')
      country = address.get('country', '')       

      if existing:
        existing.update(
          reservation_id=booking['id'],
          apartment=booking['apartment']['name'],
          arrival=datetime.strptime(booking['arrival'],"%Y-%m-%d").date(),
          departure=datetime.strptime(booking['departure'],"%Y-%m-%d").date(),
          guestname=booking['guest-name'],
          channel_name=booking['channel']['name'],
          guest_email=booking['email'],
          phone=booking['phone'],
          adults=booking['adults'],
          children=booking['children'],
          type=booking['type'],
          guestid=booking['guestId'],
          language=booking['language'],
          address_street=street,
          address_postalcode=postal_code,
          address_city=city,
          address_country=country,
          email=user_email
        )
      else:
        if booking['channel']['name'] != 'Blocked channel':
          app_tables.bookings.add_row(
            reservation_id=booking['id'],
            apartment=booking['apartment']['name'],
            arrival=datetime.strptime(booking['arrival'],"%Y-%m-%d").date(),
            departure=datetime.strptime(booking['departure'],"%Y-%m-%d").date(),
            guestname=booking['guest-name'],
            channel_name=booking['channel']['name'],
            guest_email=booking['email'],  
            phone=booking['phone'],
            adults=booking['adults'],
            children=booking['children'],
            type=booking['type'],
            guestid=booking['guestId'],
            language=booking['language'],
            address_street=street,
            address_postalcode=postal_code,
            address_city=city,
            address_country=country,
            email=user_email
          )

      bookings_added += 1
    except KeyError as e:
      print(f"Missing key in booking data: {e}")
      continue

  anvil.server.launch_background_task('save_user_apartment_count',user_email)

  return f"Erfolgreich {bookings_added} Buchungen mit Adressdaten abgerufen und gespeichert."

# Moved outside the sync_smoobu function
#def get_guest_details(guest_id, headers):
#    guest_url = f"https://login.smoobu.com/api/guests/{guest_id}"
#    response = requests.get(guest_url, headers=headers)
#    if response.status_code == 200:
#        return response.json()
#    return {}

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
