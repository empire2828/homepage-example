import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email'] 
  print(user_email)
  result= anvil.server.launch_background_task('sync_smoobu',user_email)
  return result

@anvil.server.background_task
def sync_smoobu(user_email):
    # Buchungen abrufen
    base_url = "https://login.smoobu.com/api/reservations"
    api_key = anvil.secrets.get_secret('smoobu_api_key')
    
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    params = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "confirmed",
        "page": 1,
        "limit": 100
    }
    
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
            existing = app_tables.bookings.get(reservation_id=booking['id'])
            

            # Gästedaten abrufen
            guest_data = get_guest_details(booking['guestId'], headers)
            address = guest_data.get('address', {})
            street = address.get('street', '')
            city = address.get('city', '')
            postal_code = address.get('postalCode', '')
            country = address.get('country', '')
            
            apartment_id = booking['apartment']
            guest_name = booking['guest-name']
            #current_user = anvil.users.get_user()
            #user_email = current_user['email'] 
            
            if existing:
                existing.update(
                    reservation_id=booking['id'],
                    apartment=booking['apartment']['name'],
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=guest_name,
                    channel_name=booking['channel']['name'],
                    adults=booking['adults'],
                    children=booking['children'],
                    type=booking['type'],
                    guestid=booking['guestId'],
                    address_street=street,
                    address_postalcode=postal_code,
                    address_city=city,
                    address_country=country,
                    email=user_email
                )
            else:
                app_tables.bookings.add_row(
                    reservation_id=booking['id'],
                    apartment=booking['apartment']['name'],
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=guest_name,
                    channel_name=booking['channel']['name'],
                    adults=booking['adults'],
                    children=booking['children'],
                    type=booking['type'],
                    guestid=booking['guestId'],
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
    
    return f"Erfolgreich {bookings_added} Buchungen mit Adressdaten abgerufen und gespeichert."

def get_guest_details(guestid, headers):
    """Ruft die Gästedaten für einen bestimmten Gast ab"""
    guest_url = f"https://login.smoobu.com/api/guests/{guestid}"
    
    response = requests.get(guest_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 422:
        print(f"Gast nicht gefunden für ID: {guestid}")
        return {}  # Leeres Dictionary zurückgeben, wenn der Gast nicht gefunden wurde
    else:
        print(f"Fehler beim Abrufen der Gästedaten: {response.status_code} - {response.text}")
        return {}  # Leeres Dictionary für andere Fehler zurückgeben

