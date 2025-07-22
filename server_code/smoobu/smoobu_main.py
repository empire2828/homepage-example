import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
import anvil.secrets
from google.cloud import bigquery
from google.oauth2 import service_account
import json
from Users import get_user_email

# BigQuery Konfiguration
BIGQUERY_PROJECT_ID = "lodginia"
BIGQUERY_DATASET_ID = "lodginia" 
BIGQUERY_TABLE_ID = "bookings"
FULL_TABLE_ID = "lodginia.lodginia.bookings"

@anvil.server.background_task
def get_price_elements(reservation_id, headers):
  price_data = {
    'price_baseprice': 0,
    'price_cleaningfee': 0,
    'price_longstaydiscount': 0,
    'price_coupon': 0,
    'price_addon': 0,
    'price_curr': None,
    'price_comm': 0
  }
  if reservation_id:
    price_elements_response = requests.get(
      f"https://login.smoobu.com/api/reservations/{reservation_id}/price-elements",
      headers=headers
    )
    if price_elements_response.status_code == 200:
      price_elements = price_elements_response.json().get("priceElements", [])
      #print(price_elements)

      has_addon = any(pe.get('type') == 'addon' for pe in price_elements)
      has_cleaningFee = any(pe.get('type') == 'cleaningFee' for pe in price_elements)

      for pe in price_elements:
        if pe.get('type') == 'basePrice':
          price_data['price_baseprice'] = pe.get('amount')
        elif pe.get('type') == 'cleaningFee':
          price_data['price_cleaningfee'] = pe.get('amount')
        elif pe.get('type') == 'longStayDiscount':
          price_data['price_longstaydiscount'] = pe.get('amount')
        elif pe.get('type') == 'addon':
          price_data['price_addon'] = pe.get('amount')
        elif pe.get('type') == 'coupon':
          price_data['price_coupon'] = pe.get('coupon')

        #Paymentcharge nur wenn selber angelegt manuell in Smoobu
        if pe.get('type') == 'commission' or pe.get('name') == 'PaymentCharge':
          price_data['price_comm'] += round(abs(pe.get('amount') or 0),2)

        price_data['price_curr'] = pe.get('currencyCode')

        name_lower = (pe.get('name') or '').lower()

        cleaning_terms = ['reinigung', 'cleaning']
        if not has_cleaningFee:
          if any(term in name_lower for term in cleaning_terms):
            price_data['price_cleaningfee'] += pe.get('amount') or 0

        #alles andere in None Type außer Reinigung und Cleaning zu Addon
        addon_terms = ['wäsche','linen','strom','electricity','heizung', 'heating','tax' ,'tourism','resort', 'handtuch','towel','service','resort']        
        if not has_addon:
          if any(term in name_lower for term in addon_terms):
            price_data['price_addon'] += pe.get('amount') or 0

  return price_data


#https://developers.booking.com/demand/docs/development-guide/rate-limiting

#headers = {
#  "Api-Key": anvil.secrets.get_secret('smoobu_api_key'),
#  "Content-Type": "application/json"
#}
#print('function_call:',get_price_elements('70507371',headers))

def get_bigquery_client():
  """Erstellt einen BigQuery Client mit Service Account Authentifizierung"""
  try:
    service_account_json = anvil.secrets.get_secret('bigquery_api_key')
    service_account_info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
      service_account_info,
      scopes=['https://www.googleapis.com/auth/bigquery']
    )
    client = bigquery.Client(
      credentials=credentials,
      project=service_account_info['project_id']
    )
    return client
  except Exception as e:
    print(f"Fehler beim BigQuery Client Setup: {str(e)}")
    return None

@anvil.server.background_task
def delete_booking(reservation_id, user_email):
  #user_email = get_user_email(user_id)
  if not user_email:
    print("Fehler: Benutzer-E-Mail konnte nicht ermittelt werden")
    return "Fehler: Benutzer nicht gefunden"

  bq_client = get_bigquery_client()
  if not bq_client:
    print("Fehler: BigQuery Client konnte nicht erstellt werden")
    return "Fehler: BigQuery Client Setup"

    # --- Try Hard Delete ---
  delete_stmt = f"""
        DELETE FROM `{FULL_TABLE_ID}`
        WHERE reservation_id = @res_id AND email = @mail
    """
  # Typ prüfen für reservation_id
  try:
    res_id = int(reservation_id)
    param_type = "INT64"
  except (ValueError, TypeError):
    res_id = reservation_id
    param_type = "STRING"

  try:
    job = bq_client.query(
      delete_stmt,
      job_config=bigquery.QueryJobConfig(
        query_parameters=[
          bigquery.ScalarQueryParameter("res_id", param_type, res_id),
          bigquery.ScalarQueryParameter("mail", "STRING", user_email)
        ]
      )
    )
    job.result()  # Warten bis Abschluss
    rows_affected = job.num_dml_affected_rows
    print(f"Hard delete versucht. BigQuery-Rows affected: {rows_affected}")
    # Wenn wirklich gelöscht wurde, hier fertig
    if rows_affected and rows_affected > 0:
      return f"Hard delete erfolgreich. {rows_affected} Zeile(n) gelöscht."
  except Exception as e:
    print(f"Hard delete fehlgeschlagen ({e}). Führe stattdessen soft delete aus.")

    # --- Fallback: Soft Delete ---
  update_stmt = f"""
        UPDATE `{FULL_TABLE_ID}`
        SET is_deleted = TRUE
        WHERE reservation_id = @res_id AND email = @mail
    """
  try:
    job = bq_client.query(
      update_stmt,
      job_config=bigquery.QueryJobConfig(
        query_parameters=[
          bigquery.ScalarQueryParameter("res_id", param_type, res_id),
          bigquery.ScalarQueryParameter("mail", "STRING", user_email)
        ]
      )
    )
    job.result()
    rows_affected = job.num_dml_affected_rows
    print(f"Soft delete ausgeführt. BigQuery-Rows affected: {rows_affected}")
    return f"Soft delete erfolgreich. {rows_affected} Zeile(n) aktualisiert."
  except Exception as e:
    print(f"Soft delete fehlgeschlagen: {e}")
    return f"Fehler bei löschen: {e}"
