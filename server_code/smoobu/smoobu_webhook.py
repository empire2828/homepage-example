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
        
        if action in ['newReservation', 'updateReservation', 'cancelReservation']:
            # Die eigentlichen Buchungsdaten befinden sich im 'data'-Feld
            process_booking(booking_data, user_id)            
            print(f"Buchung verarbeitet: {booking_data.get('id')}")
        
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
  supabase_key= get_supabase_key_for_user(user_email)
  reservation_id = booking_data.get('id')
  print(f"Verarbeite Buchung: ID={reservation_id}, Ankunft={booking_data.get('arrival')}, E-Mail={user_email}")

  # Blocked channel überspringen
  if booking_data.get('channel', {}).get('name') == 'Blocked channel':
    print(f"Buchung {reservation_id} ist ein Blocked channel - wird übersprungen")
    return

    # Prüfe, ob Buchung mit reservation_id UND user_email existiert
  existing = supabase_client.table("bookings").select("*").eq("reservation_id", reservation_id).eq("email", user_email).execute().data

  data = {
    "type": booking_data.get('type'),
    "arrival": booking_data.get('arrival'),
    "departure": booking_data.get('departure'),
    "created_at": booking_data.get('created-at'),
    "modified_at": booking_data.get('modifiedAt'),
    "apartment": booking_data.get('apartment', {}).get('name'),
    "guestname": booking_data.get('guest-name', ''),
    "channel_name": booking_data.get('channel', {}).get('name'),
    "adults": booking_data.get('adults'),
    "children": booking_data.get('children'),
    "language": booking_data.get('language'),
    "guestid": booking_data.get('guestId'),
    "email": user_email,
    "price": booking_data.get('price'),
    "price_paid": booking_data.get('price-paid'),
    "commission_included": booking_data.get('commission_included'),
    "prepayment": booking_data.get('prepayment'),
    "prepayment_paid": booking_data.get('prepayment-paid'),
    "deposit": booking_data.get('deposit'),
    "deposit_paid": booking_data.get('deposit-paid'),
    "reservation_id": reservation_id,
    "supabase_key": supabase_key
  }

  if existing:
    print(f"Aktualisiere bestehende Buchung: {reservation_id} für {user_email}")
    # Aktualisiere mit beiden Bedingungen
    supabase_client.table("bookings").update(data).eq("reservation_id", reservation_id).eq("email", user_email).execute()
  else:
    print(f"Füge neue Buchung hinzu: {reservation_id} für {user_email}")
    supabase_client.table("bookings").insert(data).execute()

@anvil.server.background_task
def delete_booking(reservation_id, user_id):
  if not reservation_id or not user_id:
    print("Ungültige Reservierungs-ID oder Benutzer-ID")
    return

  user_email = get_user_email(user_id)
  if not user_email:
    print(f"Keine E-Mail für Benutzer-ID {user_id} gefunden")
    return

  response = supabase_client.table("bookings").delete().eq("reservation_id", reservation_id).eq("email", user_email).execute()
  if response.data:
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

def get_supabase_key_for_user(email):
  user_row = app_tables.users.get(email=email)
  if user_row:
    result= user_row['supabase_key'] 
    return result
  else:
    return None
