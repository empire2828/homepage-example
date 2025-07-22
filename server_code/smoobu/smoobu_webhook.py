import anvil.users
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from supabase import create_client, Client
import requests
from smoobu.smoobu_main import get_price_elements, get_bigquery_client
from google.cloud import bigquery  

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
        reservation_id = booking_data.get('id')
        
        if action in ['newReservation', 'updateReservation', 'cancelReservation']:
            process_booking(booking_data, user_id)            
            print(f"Buchung verarbeitet: {booking_data.get('id')}")

        elif action in ['priceElementCreated', 'priceElementUpdated', 'priceElementDeleted']:
          process_price_element(booking_data, user_id)
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
  if booking_data.get('channel', {}).get('name') == 'Blocked channel':
    return                                                # ignore blocks

  price_data = get_price_elements(
  reservation_id = booking_data['id'],
  headers = {"Api-Key": app_tables.users.get(email=user_email)['smoobu_api_key'],
              "Content-Type": "application/json"}
  )

  row = {
    "type":               booking_data.get('type'),
    "arrival":            booking_data.get('arrival'),
    "departure":          booking_data.get('departure'),
    "created_at":         booking_data.get('created-at'),
    "modified_at":        booking_data.get('modifiedAt'),
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
    "reservation_id":     booking_data['id'],
    "price_baseprice":    price_data.get('price_baseprice'),
    "price_cleaningfee":  price_data.get('price_cleaningfee'),
    "price_longstaydiscount": price_data.get('price_longstaydiscount'),
    "price_addon":        price_data.get('price_addon'),
    "price_coupon":       price_data.get('price_coupon'),
    "price_curr":         price_data.get('price_curr'),
    "price_comm":         price_data.get('price_comm'),
  }

  # BigQuery Client initialisieren
  bq_client = get_bigquery_client()
  if not bq_client:
    return "Fehler: BigQuery Client konnte nicht erstellt werden"
  
  # --------- “Poor-man’s UPSERT” in BigQuery ------------------------
  # 1️⃣ delete possible existing record
  delete_stmt = """
        DELETE FROM `{table}`
        WHERE reservation_id = @res_id AND email = @mail
    """.format(table=FULL_TABLE_ID)

  bq_client.query(
    delete_stmt,
    job_config = bigquery.QueryJobConfig(
      query_parameters=[
        bigquery.ScalarQueryParameter("res_id", "STRING", booking_data['id']),
        bigquery.ScalarQueryParameter("mail",   "STRING", user_email)
      ]
    )
  ).result()   # wait for completion

  # 2️⃣ insert fresh row
  errors = bq_client.insert_rows_json(FULL_TABLE_ID, [row])
  if errors:
    raise RuntimeError(errors)

@anvil.server.background_task
def delete_booking(reservation_id, user_id):
  user_email = get_user_email(user_id)
  stmt = f"""
        DELETE FROM `{FULL_TABLE_ID}`
        WHERE reservation_id = @res_id AND email = @mail
    """
  
  # BigQuery Client initialisieren
  bq_client = get_bigquery_client()
  if not bq_client:
    return "Fehler: BigQuery Client konnte nicht erstellt werden"
  
  job = bq_client.query(
    stmt,
    job_config = bigquery.QueryJobConfig(
      query_parameters=[
        bigquery.ScalarQueryParameter("res_id", "STRING", reservation_id),
        bigquery.ScalarQueryParameter("mail",   "STRING", user_email)
      ]
    )
  )
  job.result()   # wait
  print(f"BigQuery-Rows affected: {job.num_dml_affected_rows}")

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

