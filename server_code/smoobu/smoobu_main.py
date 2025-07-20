import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
import anvil.secrets

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
      print(price_elements)

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

