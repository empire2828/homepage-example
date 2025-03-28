import anvil.files
from anvil.files import data_files
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets

@anvil.server.callable
def get_all_future_bookings():
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
            guest_data = get_guest_details(booking['id'], headers)
            
            # Adressdaten extrahieren
            street = guest_data.get('street', '')
            city = guest_data.get('city', '')
            postal_code = guest_data.get('postalCode', '')
            country = guest_data.get('country', '')
            
            apartment_id = booking['apartment']
            guest_name = booking['guest-name']
            
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
                    street=street,
                    city=city,
                    postal_code=postal_code,
                    country=country
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
                    street=street,
                    city=city,
                    postal_code=postal_code,
                    country=country
                )
            
            bookings_added += 1
        except KeyError as e:
            print(f"Missing key in booking data: {e}")
            continue
    
    return f"Erfolgreich {bookings_added} Buchungen mit Adressdaten abgerufen und gespeichert."

def get_guest_details(reservation_id, headers):
    """Ruft die Gästedaten für eine bestimmte Reservierung ab"""
    guest_url = f"https://login.smoobu.com/api/reservations/{reservation_id}/guest"
    
    response = requests.get(guest_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fehler beim Abrufen der Gästedaten: {response.status_code} - {response.text}")
        return {}
