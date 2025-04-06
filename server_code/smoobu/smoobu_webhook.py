import anvil.files
from anvil.files import data_files
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
        guest_data_update(user_email)
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
    user= app_tables.users.get(email=user_email)
    if user:
        api_key= user['pms_api_key']
    else:
      pass

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    guest_data = get_guest_details(booking_data['guestId'], headers)
    address = guest_data.get('address', {})
    street = address.get('street', '')
    city = address.get('city', '')
    postal_code = address.get('postalCode', '')
    country = address.get('country', '')

    if booking_data['channel']['name'] != 'Blocked channel':
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