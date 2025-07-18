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

  # 2. Die neueste Buchung bestimmen (ohne Apartment-Bezug)
  latest_booking = all_bookings[0] if all_bookings else None

  if latest_booking:
    cleaning_fee = latest_booking.get('price_cleaningfee')
    addon_fee = latest_booking.get('price_addon')
    upsert_data = {
      "email": user_email,
      "std_cleaning_fee": float(cleaning_fee) if cleaning_fee not in ("", None) else None,
      "std_linen_fee": float(addon_fee) if addon_fee not in ("", None) else None
    }
    supabase_client.table("parameter").upsert(
      [upsert_data],
      on_conflict=["email"]
    ).execute()
    print('last fees saved as std',user_email,' ',cleaning_fee,' ',addon_fee)
    return 1
  else:
    return 0

@anvil.server.background_task
def save_all_channels_for_user(user_email):
  # 1. Lade alle Buchungen für den Nutzer
  response = (
    supabase_client
      .table("bookings")
      .select("channel_name")
      .eq("email", user_email)
      .order("created_at", desc=True)
      .execute()
  )
  bookings = response.data

  # 2. Extrahiere alle einzigartigen genutzten channel_names
  #    (keine None/Leere, keine 'blocked channel')
  unique_channels = set()
  for booking in bookings:
    channel = booking.get("channel_name")
    # Ignoriere leere Werte UND 'blocked channel'
    if channel and channel.lower() != "Blocked channel":
      unique_channels.add(channel)

    # 3. Für jeden Channel: Hole std_commission_rate aus Anvil Tabelle 'channels'
  upserts = []
  for channel_name in unique_channels:
    row = anvil.tables.app_tables.channels.get(name=channel_name)
    std_commission_rate = row.get('std_commission_rate') if row else None

    upserts.append({
      "email": user_email,
      "channel_name": channel_name,
      "channel_commission": std_commission_rate
    })
    print('std channels added:', channel_name, std_commission_rate)

    # 4. Upsert in std_commission pro Channel
  if upserts:
    supabase_client.table("std_commission").upsert(
      upserts,
      on_conflict="email,channel_name"
    ).execute()
    print("Channels gespeichert:", user_email, list(unique_channels))
    return len(upserts)
  else:
    print("Keine Channels für", user_email, "gefunden.")
    return 0






