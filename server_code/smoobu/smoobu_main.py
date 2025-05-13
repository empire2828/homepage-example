import anvil.facebook.auth
import anvil.server
#import anvil.tables as tables
from anvil.tables import app_tables
import requests
#from datetime import datetime
#import anvil.secrets
#import json

@anvil.server.callable
def get_guest_details(guestid, headers):
    """Ruft die Gästedaten für einen bestimmten Gast ab"""
    guest_url = f"https://login.smoobu.com/api/guests/{guestid}"  
    response = requests.get(guest_url, headers=headers) 
    if guestid is None:
      print('Guest ID is none')
      return {}  # Leeres Dictionary zurückgeben
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 422:
        print(f"Gast nicht gefunden für ID: {guestid}")
        return {}  # Leeres Dictionary zurückgeben, wenn der Gast nicht gefunden wurde
    else:
        print(f"Fehler beim Abrufen der Gästedaten: guestid: {guestid} {response.status_code} - {response.text}")
        return {}  # Leeres Dictionary für andere Fehler zurückgeben

@anvil.server.callable
def guest_data_update(user_email):
    anvil.server.launch_background_task('update_missing_guest_data',user_email)
    return "Hintergrundtask zur Aktualisierung der Gastdaten gestartet"

@anvil.server.background_task
def update_missing_guest_data(user_email):
    user= app_tables.users.get(email=user_email)
    if user:
        api_key= user['smoobu_api_key']
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

