import anvil.server
#import anvil.tables as tables
from anvil.tables import app_tables
import requests
from supabase import create_client, Client

# Supabase-Client initialisieren
supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

def upsert_booking(data, on_conflict_fields=('reservation_id', 'email')):
  response = (
    supabase_client
      .from_("bookings")
      .upsert(data, on_conflict=",".join(on_conflict_fields))
      .execute()
  )
  return response

@anvil.server.background_task
def fetch_and_store_price_elements(reservation_id, user_id):
  try:
    user_email = get_user_email(user_id) or "unbekannt"
    user = app_tables.users.get(email=user_email)
    if not user:
      print(f"User nicht gefunden: {user_email}")
      return
    api_key = user['smoobu_api_key']
    supabase_key = user['supabase_key']

    url = f"https://login.smoobu.com/api/reservations/{reservation_id}/price-elements"
    headers = {"Api-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      print(f"Fehler beim Abrufen der priceElements: {response.status_code} - {response.text}")
      return

    api_data = response.json()
    price_elements = api_data.get("priceElements", [])
    channel_name = api_data.get("channel", {}).get("name")  # Falls vorhanden

    # --- Preisbestandteile extrahieren ---
    price_baseprice = None
    price_cleaningfee = 0
    price_longstaydiscount = None
    price_addon = 0
    price_coupon = None
    price_curr = None
    price_comm = None

    for pe in price_elements:
      typ = pe.get('type')
      amount = pe.get('amount') or 0
      if typ == 'basePrice':
        price_baseprice = amount
      elif typ == 'cleaningFee':
        price_cleaningfee += amount
      elif typ == 'longStayDiscount':
        price_longstaydiscount = amount
      elif typ == 'addon':
        price_addon += amount
      elif typ == 'coupon':
        price_coupon = amount
      elif typ == 'commission':
        price_comm = amount
      elif typ == 'channelCustom':
        if pe.get('name') in ('PASS_THROUGH_RESORT_FEE', 'PASS_THROUGH_LINEN_FEE'):
          price_addon += amount
        if channel_name == "Booking.com":
          price_cleaningfee += amount
      price_curr = pe.get('currencyCode')

    data = {
      "reservation_id": reservation_id,
      "email": user_email,
      "supabase_key": supabase_key,
      "price_baseprice": price_baseprice,
      "price_cleaningfee": price_cleaningfee,
      "price_longstaydiscount": price_longstaydiscount,
      "price_addon": price_addon,
      "price_coupon": price_coupon,
      "price_curr": price_curr,
      "price_comm": price_comm
    }

    existing = (
      supabase_client
        .table("bookings")
        .select("*")
        .eq("reservation_id", reservation_id)
        .eq("email", user_email)
        .execute()
        .data
    )

    if existing:
      print(f"Aktualisiere Buchung: {reservation_id} für {user_email}")
      supabase_client.table("bookings").update(data).eq("reservation_id", reservation_id).eq("email", user_email).execute()
    else:
      print(f"Füge neue Buchung hinzu: {reservation_id} für {user_email}")
      supabase_client.table("bookings").insert(data).execute()

  except Exception as e:
    print(f"Fehler in fetch_and_store_price_elements: {str(e)}")
