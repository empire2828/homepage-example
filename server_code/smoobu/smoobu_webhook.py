import anvil.users
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from google.cloud import bigquery
from smoobu.smoobu_main import get_price_elements
from servermain import get_bigquery_client, to_sql_value

@anvil.server.http_endpoint('/smoobu/webhook', methods=['POST'])
def smoobu_webhook_handler():
  try:
    request = anvil.server.request
    webhook_data = request.body_json
    print(f"Webhook-Daten empfangen: {webhook_data}")        

    action = webhook_data.get('action')
    booking_data = webhook_data.get('data', {})
    user_id = str(webhook_data.get('user') or 0)
    user_email = get_user_email(user_id)

    if action in ['newReservation', 'cancelReservation', 'modification of booking','updateReservation']:
      process_booking(booking_data, user_id)            
      print(f"Buchung verarbeitet: {booking_data.get('id')}")

    user_row = app_tables.users.get(email=user_email)
    if user_row:
      user_row['server_data_last_update'] = datetime.now()

    return {"status": "success"}

  except Exception as e:
    print(f"smoobu_webhook_handler: Fehler beim Verarbeiten des Webhooks: {str(e)}")
    return {"status": "error", "message": str(e)}, 500

@anvil.server.background_task
def process_booking(booking_data, user_id):
  if not booking_data or 'id' not in booking_data:
    print("process_booking: Keine gültigen Buchungsdaten erhalten")
    return

  user_email = get_user_email(user_id) or "unbekannt"
  user = app_tables.users.get(email=user_email)
  if not user:
    return

  smoobu_api_key = user['smoobu_api_key']
  reservation_id = booking_data.get('id')

  # Skip blocked channels
  channel_name = booking_data.get('channel', {}).get('name')
  if channel_name == 'Blocked channel':
    print(f"process_booking: Buchung {reservation_id} ist ein Blocked channel - wird übersprungen")
    return

  # Get price data
  headers = {"Api-Key": smoobu_api_key, "Content-Type": "application/json"}
  price_data = get_price_elements(reservation_id=reservation_id, headers=headers)
  composite_id = f"{user_email}_{reservation_id}"

  data = {
    "id": composite_id,  
    "type": booking_data.get('type'),
    "arrival": booking_data.get('arrival'),
    "departure": booking_data.get('departure'),
    "created_at": booking_data.get('created-at', '')[:10] if booking_data.get('created-at') else None,
    "modified_at": booking_data.get('modifiedAt', '')[:10] if booking_data.get('modifiedAt') else None,
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
    "supabase_key": str(user.get('supabase_key', '') or ''),
    "price_baseprice": price_data.get('price_baseprice'),
    "price_cleaningfee": price_data.get('price_cleaningfee'),
    "price_longstaydiscount": price_data.get('price_longstaydiscount'),
    "price_addon": price_data.get('price_addon'),
    "price_coupon": price_data.get('price_coupon'),
    "price_curr": price_data.get('price_curr'),
    "price_comm": price_data.get('price_comm'),
  }

  client = get_bigquery_client()

  # Check for existing booking mit der neuen composite ID
  check_sql = """
        SELECT COUNT(*) as count 
        FROM `lodginia.lodginia.bookings`
        WHERE id = @composite_id
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("composite_id", "STRING", composite_id)
    ]
  )
  row_count = list(client.query(check_sql, job_config=job_config).result())[0]["count"]
  #print("check_sql:",check_sql)
  print("row_count:",row_count)

  fields = ', '.join(data.keys())
  #values = ', '.join([to_sql_value(v) for v in data.values()])
  #set_clause = ', '.join([f"{k}={to_sql_value(v)}" for k, v in data.items()])
  string_fields = ["supabase_key", ...]
  values = ', '.join([
    to_sql_value(v, force_string=(k in string_fields)) 
    for k, v in data.items()
  ])
  set_clause = ', '.join([
    f"{k}={to_sql_value(v, force_string=(k in string_fields))}" 
    for k, v in data.items()
  ])

  if row_count:
    # Update with DML
    update_sql = f"""
        UPDATE `lodginia.lodginia.bookings`
        SET {set_clause}
        WHERE id = @composite_id
        """
    #print("update_sql:",update_sql)
    client.query(update_sql, job_config=job_config).result()
    print(f"process_booking: Aktualisiere bestehende Buchung: {composite_id}")
  else:
    # Insert with DML
    insert_sql = f"""
        INSERT INTO `lodginia.lodginia.bookings` ({fields})
        VALUES ({values})
        """
    client.query(insert_sql).result()
    print("insert_sql:",insert_sql)
    print(f"process_booking: Füge neue Buchung hinzu: {composite_id}")

@anvil.server.background_task
def delete_booking(reservation_id, user_id):
  if not reservation_id or not user_id:
    print("Ungültige Reservierungs-ID oder Benutzer-ID")
    return

  user_email = get_user_email(user_id)
  if not user_email:
    print(f"Keine E-Mail für Benutzer-ID {user_id} gefunden")
    return

    # Composite ID für delete_booking
  composite_id = f"{user_email}_{reservation_id}"
  client = get_bigquery_client()

  delete_sql = """
        DELETE FROM `lodginia.lodginia.bookings`
        WHERE id = @composite_id
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("composite_id", "STRING", composite_id)
    ]
  )

  client.query(delete_sql, job_config=job_config).result()
  print(f"Buchung {composite_id} aus BigQuery gelöscht")

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

