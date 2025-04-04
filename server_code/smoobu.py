import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets
import json

@anvil.server.callable
def launch_sync_smoobu():
  current_user = anvil.users.get_user()
  user_email = current_user['email'] 
  print(user_email)
  result= anvil.server.launch_background_task('sync_smoobu',user_email)
  save_smoobu_userid()
  guest_data_update()
  return result

@anvil.server.background_task
def sync_smoobu(user_email):
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

#------------------------------------------------------------------------------------------------------------------------
#https://guestscreener.com/_/api/smoobu/webhook
@anvil.server.http_endpoint('/smoobu/webhook', methods=['POST'])
def smoobu_webhook_handler():
    try:
        request = anvil.server.request
        webhook_data = request.body_json
        print(f"Webhook-Daten empfangen: {webhook_data}")
        
        # Prüfen, ob es sich um eine Buchungsoperation handelt
        action = webhook_data.get('action')
        booking_data = webhook_data.get('data', {})
        user_id = webhook_data.get('user')  # Smoobu-Benutzer-ID
      
        if action in ['newReservation', 'updateReservation']:
            # Die eigentlichen Buchungsdaten befinden sich im 'data'-Feld
            process_booking(booking_data, str(user_id))
            print(f"Buchung verarbeitet: {booking_data.get('id')}")     
        elif action == 'cancelReservation':
            delete_booking(booking_data.get('id'))
            print(f"Buchung gelöscht: {booking_data.get('id')}")
        # bei jedem Aufruf des Webhooks schauen ob Gastdaten sich geändert haben (bei Direktbuchungen erst nach Anlage Buchung)
        guest_data_update()
        return {"status": "success"}
    except Exception as e:
        print(f"Fehler beim Verarbeiten des Webhooks: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

def process_booking(booking_data, user_id):
    if not booking_data or 'id' not in booking_data:
        print("Keine gültigen Buchungsdaten erhalten")
        return
    
    # Suche nach der E-Mail des Benutzers anhand der Smoobu-ID
    user_email = None
    user_row = app_tables.users.get(pms_userid=user_id)
    if user_row:
        user_email = user_row['email']
        print(f"Benutzer gefunden: {user_email}")
    else:
        print(f"Kein Benutzer mit Smoobu-ID {user_id} gefunden")
    
    # Füge einen Debug-Print hinzu, um die Werte zu sehen
    print(f"Füge Buchung hinzu: ID={booking_data.get('id')}, Ankunft={booking_data.get('arrival')}, E-Mail={user_email}")

    # Gästedaten abrufen
    headers = {
        "Api-Key": anvil.secrets.get_secret('smoobu_api_key'),
        "Content-Type": "application/json"
    }
    guest_data = get_guest_details(booking_data['guestId'], headers)
    address = guest_data.get('address', {})
    street = address.get('street', '')
    city = address.get('city', '')
    postal_code = address.get('postalCode', '')
    country = address.get('country', '')
    
    app_tables.bookings.add_row(
        arrival=booking_data.get('arrival'),
        departure=booking_data.get('departure'),
        apartment=booking_data.get('apartment', {}).get('name'),
        guestname=booking_data.get('guest-name', ''),
        reservation_id=booking_data.get('id'),
        channel_name=booking_data.get('channel', {}).get('name'),
        adults=booking_data.get('adults'),
        children=booking_data.get('children'),
        language=booking_data.get('language'),
        guestid=booking_data.get('guestId'),
        address_street=street,
        address_postalcode=postal_code,
        address_city=city,
        address_country=country,
        email=user_email  
    )

def save_smoobu_userid():
    pms_userid = str(get_smoobu_userid())
    current_user = anvil.users.get_user()
    app_tables.users.get(email=current_user['email']).update(pms_userid=pms_userid)
    return 

def get_smoobu_userid():
    headers = {
        "Api-Key": anvil.secrets.get_secret('smoobu_api_key'),
        "Cache-Control": "no-cache"
    }
  
    response = requests.get("https://login.smoobu.com/api/me", headers=headers)
  
    if response.status_code == 200:
        data = response.json()
        return data['id']
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

def delete_booking(reservation_id):
    """Löscht eine Buchung aus der Datenbank anhand der Reservierungs-ID"""
    if not reservation_id:
        print("Keine gültige Reservierungs-ID erhalten")
        return
    
    # Suche nach der Buchung in der Datenbank
    booking = app_tables.bookings.get(reservation_id=reservation_id)
    
    if booking:
        # Buchung löschen
        booking.delete()
        print(f"Buchung mit ID {reservation_id} erfolgreich gelöscht")
    else:
        print(f"Keine Buchung mit Reservierungs-ID {reservation_id} gefunden")
#-----------------------------------------------------------------------------------------
@anvil.server.callable
def guest_data_update():
    anvil.server.launch_background_task('update_missing_guest_data')
    return "Hintergrundtask zur Aktualisierung der Gastdaten gestartet"

@anvil.server.background_task
def update_missing_guest_data():
    # API-Schlüssel aus den Anvil-Secrets abrufen
    api_key = anvil.secrets.get_secret('smoobu_api_key')
    
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