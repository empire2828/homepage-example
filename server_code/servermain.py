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
  # 1. Hole alle Buchungen für diesen Nutzer in den relevanten Kanälen
  response = (
    supabase_client
      .table("bookings")
      .select("*")
      .eq("email", user_email)
      .in_("channel_name", ["Direct booking", "Website"])
      .order("apartment_id", "asc")
      .order("created_at", "desc")
      .execute()
  )
  all_bookings = response.data

  # 2. Pro Apartment die neueste Buchung für diesen User bestimmen
  latest_bookings = {}
  for b in all_bookings:
    apartment_id = b["apartment_id"]
    if apartment_id not in latest_bookings:
      latest_bookings[apartment_id] = b  # Nur erste nach created_at DESC

    # 3. Upsert in 'apartment_last_bookings'
  upserts = []
  for apartment_id, booking in latest_bookings.items():
    upserts.append({
      "apartment_id": apartment_id,
      "user_email": user_email,
      "booking_id": booking["id"],
      "created_at": booking["created_at"],
      # Optional: Felder wie Cleaning Fee etc.
    })

  if upserts:
    supabase_client.table("apartment_last_bookings").upsert(
      upserts,
      on_conflict=["apartment_id", "user_email"]
    ).execute()

  return len(upserts)  # Anzahl aktualisierter Einträge



