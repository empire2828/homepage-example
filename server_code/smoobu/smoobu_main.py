import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
import anvil.secrets
from admin import log

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

      print("[smoobu main] get_price_elements Reservation-ID",reservation_id," price_elements_response:",price_elements_response)
      log(price_elements,reservation_id,"[smoobu_main] get_price_elements")
      
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
          price_data['price_addon'] = pe.get('amount')* (pe.get('quantity') or 0)
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

@anvil.server.callable
def validate_smoobu_api_key(user_email):
  user = app_tables.users.get(email=user_email)
  if not user:
    return {"valid": False, "error": "Benutzer nicht gefunden"}
  api_key = user['smoobu_api_key']
  if not api_key:
    return {"valid": False, "error": "Kein API-Key hinterlegt"}

  headers = {
    "Api-Key": api_key,
    "Cache-Control": "no-cache"
  }    
  try:
    response = requests.get("https://login.smoobu.com/api/me", headers=headers)
    if response.status_code == 200:
      data = response.json()
      return {"valid": True, "user_id": data['id']}
    elif response.status_code == 401:
      return {"valid": False, "error": "API-Key ist ungültig oder abgelaufen"}
    else:
      return {"valid": False, "error": f"API-Fehler: {response.status_code}"}
  except Exception as e:
    return {"valid": False, "error": f"Verbindungsfehler: {str(e)}"}


