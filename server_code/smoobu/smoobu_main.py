import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from supabase import create_client, Client
from admin import log

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

#https://legacy.developers.booking.com/api/commercial/index.html?page_url=possible-values

@anvil.server.background_task
def get_price_elements(reservation_id, headers):
  price_data = {
    'price_baseprice': None,
    'price_cleaningfee': 0,
    'price_longstaydiscount': None,
    'price_coupon': None,
    'price_addon': 0,
    'price_curr': None,
    'price_comm': None
  }
  
  if reservation_id:
    price_elements_response = requests.get(
      f"https://login.smoobu.com/api/reservations/{reservation_id}/price-elements",
      headers=headers
    )
    if price_elements_response.status_code == 200:
      price_elements = price_elements_response.json().get("priceElements", [])
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

        if pe.get('type') == 'commission':
          price_data['price_comm'] = pe.get('amount')

        if pe.get('type') == 'channelCustom' and \
        (pe.get('name') == 'PASS_THROUGH_RESORT_FEE' or pe.get('name') == 'PASS_THROUGH_LINEN_FEE'):
          price_data['price_addon'] += pe.get('amount') or 0

        price_data['price_curr'] = pe.get('currencyCode')

        terms = ['reinigung', 'cleaning']
        if price_data['price_cleaningfee'] == 0:
          if pe.get('name', '').lower() in [term.lower() for term in terms]:
            price_data['price_cleaningfee'] = pe.get('amount', 0) + price_data['price_cleaningfee']

        terms = ['wäsche', 'linen', 'strom', 'electricity', 'heizung', 'heating' , 'tax' , 'tourism']
        if price_data['price_addon'] == 0:
          if pe.get('name', '').lower() in [term.lower() for term in terms]:
            price_data['price_addon'] = pe.get('amount', 0) + price_data['price_addon']

  return price_data





