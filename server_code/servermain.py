import anvil.email
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import time
from datetime import datetime, timedelta, timezone
from . import routes # noqa: F401
from supabase import create_client, Client
import anvil.secrets

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

# Supabase-Client initialisieren
supabase: Client = create_client(supabase_url, supabase_api_key)

@anvil.server.callable
def delete_bookings_by_email(user_email):
  resp = (
    supabase.table("bookings")
      .delete()
      .eq("email", user_email)
      .execute()
  )
  return {
    "status": "success",
    "deleted_count": len(resp.data),
    "deleted_data": resp.data,
  }

@anvil.server.callable
def send_registration_notification(user_email):
  anvil.email.send(
    to="dirk.klemer@gmail.com",  # Deine eigene Adresse
    subject="Neuer Benutzer registriert für Lodginia.com",
    text=f"Ein neuer Benutzer hat sich registriert: {user_email}"
  )
    
@anvil.server.callable
def send_email_to_support(text, file=None, email=None):
  attachments = []
  if file is not None:
    attachments.append(file)
  try:
    anvil.email.send(
      to="dirk.klemer@gmail.com",
      subject="Neue Supportanfragen vom Lodginia.com",
      text=text + "\n\n" + str(email),
      attachments=attachments
    )
    print("send_email_to_support: success", email, text)
  except Exception as e:
    print("send_email_to_support: ERROR", e)

@anvil.server.callable
def save_user_parameter(std_cleaning_fee=None, std_linen_fee=None,use_own_std_fees=False):
  current_user = anvil.users.get_user()
  email = current_user['email']
  supabase_key = current_user['supabase_key']
  try:
    current_user['std_cleaning_fee']=  float(std_cleaning_fee)
    current_user['std_linen_fee']= float(std_linen_fee)
    current_user['use_own_std_fees']= use_own_std_fees
  except ValueError:
    return None
    
  data = {
    "supabase_key": supabase_key,
    "std_cleaning_fee": std_cleaning_fee,
    "std_linen_fee": std_linen_fee,
    "use_own_std_fees": use_own_std_fees,
    "email": email
  }
  response = supabase.table("parameter").upsert(
    [data],
    on_conflict="email"  # Konfliktspalte angeben!
  ).execute()
  return response.data  # oder True/False je nach Bedarf
  
  pass

@anvil.server.background_task
def save_last_fees_as_std(user_email):
  # 1. Letzte Buchung des Nutzers im Kanal 'Direct booking' oder 'Website' holen
  response = (
    supabase_client.table("bookings")
      .select("*")
      .eq("email", user_email)
      .in_("channel_name", ["Direct booking", "Website"])
      .order("created_at", desc=True)
      .limit(1)
      .execute()
  )
  bookings = response.data
  if not bookings:
    return None

  latest_booking = bookings[0]
  # 2. Preiselemente auslesen (angenommen, als JSON oder Liste in 'price_elements')
  price_elements = latest_booking.get("price_elements", [])
  cleaning_fee = None
  for element in price_elements:
    if element.get("type") == "cleaningFee":
      cleaning_fee = element.get("amount")
      break

    # 3. Wert in Anvil Users-Tabelle speichern
  if cleaning_fee is not None:
    user_row = app_tables.users.get(email=user_email)
    if user_row is not None:
      user_row['std_cleaning_fee'] = cleaning_fee

  return cleaning_fee
