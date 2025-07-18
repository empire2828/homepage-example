import anvil.users
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from supabase import create_client, Client
import requests
from smoobu.smoobu_main import get_price_elements

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

        elif action in ['priceElementCreated', 'priceElementUpdated']:
          process_price_element(booking_data, user_id)
          print(f"PriceElement verarbeitet: {booking_data.get('id')}")

        if action in ['newReservation']:
          # bei NewReservation fehlen die priceElements, bei UpdateReservation kommen diese mit
          fetch_and_store_price_elements(reservation_id, user_id)            
        
        user_row = app_tables.users.get(email=user_email)
        if user_row:
            user_row['server_data_last_update'] = datetime.now()

        return {"status": "success"} 
  
    except Exception as e:
        print(f"Fehler beim Verarbeiten des Webhooks: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

# updatReservation liefert price_elements mit, newReservation nicht
@anvil.server.background_task
def process_booking(booking_data, user_id):
  if not booking_data or 'id' not in booking_data:
    print("Keine gültigen Buchungsdaten erhalten")
    return
  try:
    user_email = get_user_email(user_id) or "unbekannt"
    user= app_tables.users.get(email=user_email)
    if user:
      smoobu_api_key= user['smoobu_api_key']
      supabase_key = user['supabase_key']
    else:
      pass
  reservation_id = booking_data.get('id')
  print(f"Verarbeite Buchung: ID={reservation_id}, Ankunft={booking_data.get('arrival')}, E-Mail={user_email}")

  # Skip blocked channels
  if booking_data.get('channel', {}).get('name') == 'Blocked channel':
    print(f"Buchung {reservation_id} ist ein Blocked channel - wird übersprungen")
    return

    # Check for existing booking
  existing = supabase_client.table("bookings") \
    .select("*") \
    .eq("reservation_id", reservation_id) \
    .eq("email", user_email) \
    .execute().data

  channel_name = booking_data.get('channel', {}).get('name')
  headers = {
    "Api-Key": smoobu_api_key,
    "Content-Type": "application/json"
  }

  # Always use the get_price_elements function
  price_data = get_price_elements(
    reservation_id=reservation_id,
    headers=headers,
    price_elements=booking_data.get('priceElements', None)  # Pass if present, else None
  )

  data = {
    "type": booking_data.get('type'),
    "arrival": booking_data.get('arrival'),
    "departure": booking_data.get('departure'),
    "created_at": booking_data.get('created-at'),
    "modified_at": booking_data.get('modifiedAt'),
    "apartment": booking_data.get('apartment', {}).get('name'),
    "guestname": booking_data.get('guest-name', ''),
    "channel_name": channel_name,
    "adults": booking_data.get('adults'),
    "children": booking_data.get('children'),
    "language": booking_data.get('language'),
    "guestid": booking_data.get('guestId'),
    "email": user_email,
    "price": booking_data.get('price'),
    "price_paid": booking_data.get('price-paid'),
    "commission_included": booking_data.get('commission-included'),
    "prepayment": booking_data.get('prepayment'),
    "prepayment_paid": booking_data.get('prepayment-paid'),
    "deposit": booking_data.get('deposit'),
    "deposit_paid": booking_data.get('deposit-paid'),
    "reservation_id": reservation_id,
    "supabase_key": supabase_key,
    "price_baseprice": price_data.get('price_baseprice'),
    "price_cleaningfee": price_data.get('price_cleaningfee'),
    "price_longstaydiscount": price_data.get('price_longstaydiscount'),
    "price_addon": price_data.get('price_addon'),
    "price_coupon": price_data.get('price_coupon'),
    "price_curr": price_data.get('price_curr'),
    "price_comm": price_data.get('price_comm'),
  }

  if existing:
    print(f"Aktualisiere bestehende Buchung: {reservation_id} für {user_email}")
    print(data)
    supabase_client.table("bookings").update(data) \
      .eq("reservation_id", reservation_id) \
      .eq("email", user_email) \
      .execute()
  else:
    print(f"Füge neue Buchung hinzu: {reservation_id} für {user_email}")
    print(data)
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

