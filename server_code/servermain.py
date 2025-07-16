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



@anvil.server.background_task
def save_last_fees_as_std(user_email):
  # 1. Hole alle Buchungen für diesen Nutzer in den relevanten Kanälen
  response = (
    supabase_client
      .table("bookings")
      .select("*")
      .eq("email", user_email)
      .in_("channel_name", ["Direct booking", "Website"])
      .order("created_at", desc=True)
      .execute()
  )
  all_bookings = response.data

  # 2. Pro Apartment die neueste Buchung für diesen User bestimmen
  latest_bookings = {}
  for b in all_bookings:
    apartment = b["apartment"]
    if apartment not in latest_bookings:
      latest_bookings[apartment] = b

    # 3. Upsert in 'parameter'
  upserts = []
  for apartment, booking in latest_bookings.items():
    upserts.append({
      "apartment": apartment,
      "email": user_email,
      "std_cleaning_fee": booking['price_cleaningfee'],
      # Optional: weitere Felder wie Cleaning Fee etc.
    })

  if upserts:
    supabase_client.table("parameter").upsert(
      upserts,
      on_conflict=["email"]  # Auch hier 'apartment' verwenden!
    ).execute()

  return len(upserts)




