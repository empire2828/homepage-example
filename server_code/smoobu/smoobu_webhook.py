import anvil.users
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from supabase import create_client, Client

# Supabase-Client initialisieren
supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.http_endpoint('/smoobu/webhook', methods=['POST'])
def smoobu_webhook_handler():
    try:
        request = anvil.server.request
        webhook_data = request.body_json
        print(f"Webhook-Daten empfangen: {webhook_data}")        
        # Prüfen, ob es sich um eine Buchungsoperation handelt
        action = webhook_data.get('action')
        booking_data = webhook_data.get('data', {})
        user_id = str(webhook_data.get('user') or 0)  # Smoobu-Benutzer-ID      
        user_email = get_user_email(user_id)
        reservation_id = booking_data.get('id')
        
        if action in ['newReservation', 'updateReservation']:
            # Die eigentlichen Buchungsdaten befinden sich im 'data'-Feld
            process_booking(booking_data, user_id)            
            print(f"Buchung verarbeitet: {booking_data.get('id')}")

        elif action == 'cancelReservation':
            delete_booking(booking_data.get('id'), webhook_data.get('user'))
            print(f"Buchung gelöscht: {booking_data.get('id')} ",webhook_data.get('user'))
        
        user_row = app_tables.users.get(email=user_email)
        if user_row:
            user_row['server_data_last_update'] = datetime.now()

        return {"status": "success"} 
  
    except Exception as e:
        print(f"Fehler beim Verarbeiten des Webhooks: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

@anvil.server.background_task
def process_booking(booking_data, user_id):
    if not booking_data or 'id' not in booking_data:
        print("Keine gültigen Buchungsdaten erhalten")
        return
    
    user_email = get_user_email(user_id) or "unbekannt"
    reservation_id = booking_data.get('id')
    
    # Füge einen Debug-Print hinzu, um die Werte zu sehen
    print(f"Verarbeite Buchung: ID={reservation_id}, Ankunft={booking_data.get('arrival')}, E-Mail={user_email}")
    
    # Gästedaten abrufen
    user = app_tables.users.get(email=user_email)
    if user:
        api_key = user['smoobu_api_key']
    else:
        print(f"Kein Benutzer mit E-Mail {user_email} gefunden")
        return

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Ignoriere Buchungen vom Blocked channel
    if booking_data['channel']['name'] == 'Blocked channel':
        print(f"Buchung {reservation_id} ist ein Blocked channel - wird übersprungen")
        return
    
    # Prüfe, ob die Buchung bereits existiert
    existing_booking = app_tables.bookings.get(reservation_id=reservation_id)
    
    if existing_booking:
        # Aktualisiere die bestehende Buchung
        print(f"Aktualisiere bestehende Buchung: {reservation_id}")
        existing_booking.update(
            arrival=datetime.strptime(booking_data['arrival'],"%Y-%m-%d").date(),
            departure=datetime.strptime(booking_data['departure'],"%Y-%m-%d").date(),
            apartment=booking_data.get('apartment', {}).get('name'),
            guestname=booking_data.get('guest-name', ''),
            channel_name=booking_data.get('channel', {}).get('name'),
            guest_email=booking_data.get('email'),
            phone=booking_data.get('phone'),
            adults=booking_data.get('adults'),
            children=booking_data.get('children'),
            language=booking_data.get('language'),
            guestid=booking_data.get('guestId'),
        )
    else:
        # Füge eine neue Buchung hinzu
        print(f"Füge neue Buchung hinzu: {reservation_id}")
        app_tables.bookings.add_row(
            arrival=datetime.strptime(booking_data['arrival'],"%Y-%m-%d").date(),
            departure=datetime.strptime(booking_data['departure'],"%Y-%m-%d").date(),
            apartment=booking_data.get('apartment', {}).get('name'),
            guestname=booking_data.get('guest-name', ''),
            reservation_id=reservation_id,
            channel_name=booking_data.get('channel', {}).get('name'),
            guest_email=booking_data.get('email'),  
            phone=booking_data.get('phone'),
            adults=booking_data.get('adults'),
            children=booking_data.get('children'),
            language=booking_data.get('language'),
            guestid=booking_data.get('guestId'),
            email=user_email
        )

@anvil.server.background_task
def delete_booking(reservation_id, user_id):
    """Löscht eine Buchung aus der Datenbank anhand der Reservierungs-ID und Benutzer-ID"""
    if not reservation_id or not user_id:
        print("Ungültige Reservierungs-ID oder Benutzer-ID")
        return
    
    # Hole die Benutzer-E-Mail anhand der Smoobu-Benutzer-ID
    user_email = get_user_email(user_id)
    if not user_email:
        print(f"Keine E-Mail für Benutzer-ID {user_id} gefunden")
        return
    
    # Suche nach der Buchung mit Reservierungs-ID UND Benutzer-E-Mail
    booking = app_tables.bookings.get(
        reservation_id=reservation_id,
        email=user_email  # Voraussetzung: Spalte "email" in der Buchungstabelle
    )
    
    if booking:
        booking.delete()
        print(f"Buchung {reservation_id} für Benutzer {user_email} gelöscht")
    else:
        print(f"Keine Buchung mit ID {reservation_id} für Benutzer {user_email} gefunden")

@anvil.server.background_task
def get_user_email(user_id):
    user_email = None
    # Suche alle Zeilen mit dieser user_id
    user_rows = app_tables.users.search(smoobu_userid=str(user_id))
    # Explizit einen Iterator erzeugen
    first_row = next(iter(user_rows), None)
    if first_row:
        user_email = first_row['email']
        print(f"Benutzer gefunden: {user_email}")
    else:
        print(f"Kein Benutzer mit Smoobu-ID {user_id} gefunden")
    return user_email


