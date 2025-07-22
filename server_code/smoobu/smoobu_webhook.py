import anvil.users
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from supabase import create_client, Client
import requests
from smoobu.smoobu_main import get_price_elements, get_bigquery_client, delete_booking
from google.cloud import bigquery 
from Users import get_supabase_key_for_user

# BigQuery Konfiguration
BIGQUERY_PROJECT_ID = "lodginia"
BIGQUERY_DATASET_ID = "lodginia" 
BIGQUERY_TABLE_ID = "bookings"
FULL_TABLE_ID = "lodginia.lodginia.bookings"

@anvil.server.http_endpoint('/smoobu/webhook', methods=['POST'])
def smoobu_webhook_handler():
    try:
        request = anvil.server.request
        webhook_data = request.body_json
        print(f"Webhook-Daten empfangen: {webhook_data}")        
        action = webhook_data.get('action')
        booking_data = webhook_data.get('data', {})
        user_id = str(webhook_data.get('user') or 0)  # Smoobu-Benutzer-ID      
        user_email = get_user_email(user_id)
        #supabase_key= get_supabase_key_for_user(user_email)
        reservation_id = booking_data.get('id')
        
        if action in ['newReservation', 'updateReservation', 'cancelReservation']:
            process_booking(booking_data, user_id)            
            print(f"Buchung verarbeitet Reservation-ID: {booking_data.get('id')} ",booking_data.get('guest-name'))

        elif action in ['priceElementCreated', 'priceElementUpdated', 'priceElementDeleted']:
          sync_booking_by_price_element_webhook(reservation_id, user_email)
          print(f"PriceElement verarbeitet: {booking_data.get('id')}")     
        
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
    return
  user_email = get_user_email(user_id) or "unbekannt"
  print('process booking for ',user_email)
  if user_email:
      supabase_key= get_supabase_key_for_user(user_email)
  if booking_data.get('channel', {}).get('name') == 'Blocked channel':
    return                                                # ignore blocks

  reservation_id = int(booking_data['id'])
  
  price_data = get_price_elements(
    reservation_id,
    headers = {"Api-Key": app_tables.users.get(email=user_email)['smoobu_api_key'],
                "Content-Type": "application/json"}
    )

  row = {
    "type":               booking_data.get('type'),
    "arrival":            booking_data.get('arrival'),
    "departure":          booking_data.get('departure'),
    "created_at":         booking_data.get('created-at', '')[:10],
    "modified_at":        booking_data.get('modifiedAt', '')[:10],
    "apartment":          booking_data.get('apartment', {}).get('name'),
    "guestname":          booking_data.get('guest-name', ''),
    "channel_name":       booking_data.get('channel', {}).get('name'),
    "adults":             booking_data.get('adults'),
    "children":           booking_data.get('children'),
    "language":           booking_data.get('language'),
    "guestid":            booking_data.get('guestId'),
    "email":              user_email,
    "price":              booking_data.get('price'),
    "price_paid":         booking_data.get('price-paid'),
    "commission_included":booking_data.get('commission-included'),
    "prepayment":         booking_data.get('prepayment'),
    "prepayment_paid":    booking_data.get('prepayment-paid'),
    "deposit":            booking_data.get('deposit'),
    "deposit_paid":       booking_data.get('deposit-paid'),
    "reservation_id":     int(booking_data['id']),
    "price_baseprice":    price_data.get('price_baseprice'),
    "price_cleaningfee":  price_data.get('price_cleaningfee'),
    "price_longstaydiscount": price_data.get('price_longstaydiscount'),
    "price_addon":        price_data.get('price_addon'),
    "price_coupon":       price_data.get('price_coupon'),
    "price_curr":         price_data.get('price_curr'),
    "price_comm":         price_data.get('price_comm'),
    "id": f"{user_email}_{reservation_id}",
    "supabase_key":       supabase_key
  }

  # BigQuery Client initialisieren
  bq_client = get_bigquery_client()
  if not bq_client:
    return "Fehler: BigQuery Client konnte nicht erstellt werden"

  # 1 delete old row
  delete_booking(reservation_id, user_email)

  # 2️ insert fresh row
  errors = bq_client.insert_rows_json(FULL_TABLE_ID, [row])
  if errors:
    raise RuntimeError(errors)

@anvil.server.background_task
def get_user_email(user_id):
    user_email = None
    # Suche alle Zeilen mit dieser user_id
    user_rows = app_tables.users.search(smoobu_userid=str(user_id))
    # Explizit einen Iterator erzeugen
    first_row = next(iter(user_rows), None)
    if first_row:
        user_email = first_row['email']
    else:
        print(f"Kein Benutzer mit Smoobu-ID {user_id} gefunden")
    return user_email

@anvil.server.background_task
def fetch_booking_by_reservation_id(user_email, reservation_id):
  user = app_tables.users.get(email=user_email)
  if not user:
    print(f"Kein Benutzer mit der E-Mail {user_email} gefunden")
    return None

  api_key = user['smoobu_api_key']
  headers = {
    "Api-Key": api_key,
    "Content-Type": "application/json"
  }
  url = f"https://login.smoobu.com/api/reservations/{reservation_id}"

  response = requests.get(url, headers=headers)
  if response.status_code != 200:
    print(f"Buchung konnte nicht von Smoobu geladen werden: {response.status_code} - {response.text}")
    return None

  booking = response.json()
  price_data = get_price_elements(reservation_id, headers)

  row = {
    "reservation_id": str(booking.get('id')),
    "apartment": booking.get('apartment', {}).get('name', ''),
    "arrival": booking.get('arrival', '')[:10],  # Nur Datum
    "departure": booking.get('departure', '')[:10],
    "created_at": booking.get('created-at', '')[:10],
    "modified_at": booking.get('modifiedAt', '')[:10],
    "guestname": booking.get('guest-name', ''),
    "channel_name": booking.get('channel', {}).get('name', ''),
    "guest_email": booking.get('email', ''),
    "phone": booking.get('phone', ''),
    "adults": booking.get('adults', 0),
    "children": booking.get('children', 0),
    "type": booking.get('type', ''),
    "price": float(booking.get('price', 0.0)),
    "price_paid": booking.get('price-paid', ''),
    "prepayment": float(booking.get('prepayment', 0.0)),
    "prepayment_paid": booking.get('prepayment-paid', ''),
    "deposit": float(booking.get('deposit', 0.0)),
    "deposit_paid": booking.get('deposit-paid', ''),
    "commission_included": float(booking.get('commission-included', 0.0)) if booking.get('commission-included') is not None else 0.0,
    "guestid": int(booking.get('guestId', 0)),
    "language": booking.get('language', ''),
    "email": user_email,
    "supabase_key": user.get('supabase_key', ''),
    "price_baseprice": float(price_data['price_baseprice']) if price_data['price_baseprice'] else 0.0,
    "price_cleaningfee": float(price_data['price_cleaningfee']) if price_data['price_cleaningfee'] else 0.0,
    "price_longstaydiscount": float(price_data['price_longstaydiscount']) if price_data['price_longstaydiscount'] else 0.0,
    "price_coupon": float(price_data['price_coupon']) if price_data['price_coupon'] else 0.0,
    "price_addon": float(price_data['price_addon']) if price_data['price_addon'] else 0.0,
    "price_curr": price_data['price_curr'] or '',
    "price_comm": float(price_data['price_comm']) if price_data['price_comm'] else 0.0,
    "id": f"{user_email}_{reservation_id}"
  }
  return row

@anvil.server.background_task
def sync_booking_by_price_element_webhook(reservation_id, user_email):
  row = fetch_booking_by_reservation_id(user_email, reservation_id)
  if not row:
    print(f"Buchungsdaten konnten nicht geladen werden für {reservation_id}")
    return

  bq_client = get_bigquery_client()
  if not bq_client:
    print("Fehler: BigQuery Client konnte nicht erstellt werden")
    return
  
  delete_booking(reservation_id, user_email)

  errors = bq_client.insert_rows_json(FULL_TABLE_ID, [row])
  if errors:
    raise RuntimeError(errors)
