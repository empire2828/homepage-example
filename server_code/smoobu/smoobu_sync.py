import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests
from smoobu import get_guest_details, get_smoobu_userid

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email'] 
  print(user_email)
  result= anvil.server.launch_background_task('sync_smoobu',user_email)
  save_smoobu_userid(user_email)
  guest_data_update(user_email)
  return result

@anvil.server.background_task
def sync_smoobu(user_email):
    base_url = "https://login.smoobu.com/api/reservations"
    user= app_tables.users.get(email=user_email)
    if user:
        api_key= user['pms_api_key']
    else:
      pass
      
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
            
            if existing:
                existing.update(
                    reservation_id=booking['id'],
                    apartment=booking['apartment']['name'],
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=booking['guest-name'],
                    channel_name=booking['channel']['name'],
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
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=booking['guest-name'],
                    channel_name=booking['channel']['name'],
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
    
    return f"Erfolgreich {bookings_added} Buchungen mit Adressdaten abgerufen und gespeichert."

def save_smoobu_userid(user_email):
    pms_userid = str(get_smoobu_userid(user_email))
    current_user = anvil.users.get_user()
    app_tables.users.get(email=current_user['email']).update(pms_userid=pms_userid)
    return 

@anvil.server.callable
def guest_data_update(user_email):
    anvil.server.launch_background_task('update_missing_guest_data',user_email)
    return "Hintergrundtask zur Aktualisierung der Gastdaten gestartet"

@anvil.server.background_task
def update_missing_guest_data(user_email):
    user= app_tables.users.get(email=user_email)
    if user:
        api_key= user['pms_api_key']
    else:
      pass   
    # Alle Buchungen abrufen, bei denen Gastdaten fehlen
    bookings_with_missing_data = app_tables.bookings.search(
        address_street=None,
        address_postalcode=None,
        address_city=None,
        address_country=None
    )
    
    for booking in bookings_with_missing_data:
        # Gast-ID aus der Buchung abrufen
        guest_id = booking['guestid']
        
        if guest_id:
            # Gastdaten von Smoobu API abrufen
            headers = {
                "Api-Key": api_key,
                "Content-Type": "application/json"
            }
            response = requests.get(f"https://login.smoobu.com/api/guests/{guest_id}", headers=headers)
            
            if response.status_code == 200:
                guest_data = response.json()
                address = guest_data.get('address', {})
                
                # Buchung mit den abgerufenen Gastdaten aktualisieren
                booking.update(
                    address_street=address.get('street', ''),
                    address_postalcode=address.get('postalCode', ''),
                    address_city=address.get('city', ''),
                    address_country=address.get('country', '')
                )
                print(f"Gastdaten für Buchung {booking['reservation_id']} aktualisiert")
            elif response.status_code == 422:
                print(f"Gast nicht gefunden für ID: {guest_id}")
            else:
                print(f"Fehler beim Abrufen der Gästedaten: {response.status_code} - {response.text}")
        else:
            print(f"Keine Gast-ID für Buchung {booking['reservation_id']} vorhanden")
    
    print("Aktualisierung der fehlenden Gastdaten abgeschlossen")