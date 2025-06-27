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

@anvil.server.background_task
def send_result_email(user_email, reservation_id):
  # Buchung jetzt ausschließlich aus Supabase holen
  booking = fetch_booking(user_email, reservation_id)
  if not booking:
    print("Keine Buchung gefunden", user_email, reservation_id)
    return False

  # -------- Ergebnis-Aufbereitung (unverändert) --------
  openai_job = booking.get("screener_openai_job")
  email_text_ai = (
    "OpenAI: Keine Ergebnisse<br>"
    if openai_job is None
    else f"OpenAI: {openai_job}<br><br>"
  )

  linkedin_check = booking.get("screener_google_linkedin")
  email_text_linkedin = (
    "LinkedIn: Keine Ergebnisse<br>"
    if linkedin_check is None
    else f"LinkedIn: {linkedin_check}<br><br>"
  )

  address_check = booking.get("screener_address_check")
  email_text_address = (
    "Adresscheck: Keine Ergebnisse<br>"
    if address_check is None
    else f"Adresscheck: {'Erfolgreich' if address_check else 'Fehlgeschlagen'}<br><br>"
  )

  phone_check = booking.get("screener_phone_check")
  email_text_phone = (
    "Phone check: Keine Ergebnisse<br>"
    if phone_check is None
    else f"Phone check: {'Erfolgreich' if phone_check else 'Fehlgeschlagen'}<br><br>"
  )

  guestname = booking.get("guestname", "")
  arrival = booking.get("arrival", "")
  departure = booking.get("departure", "")
  bookingdata = f"{guestname} {arrival} - {departure}"

  intro_text = f"Hier kommen die Lodginia Ergebnisse für die neue Buchung: {bookingdata}<br><br><br>"
  disclaimer_text = "Die Ergebnisse können insbesondere bei häufig vorkommenen Namen falsch sein.<br><br><br>"
  url_text = "Lodginia.com"

  html_body = (
    intro_text
    + email_text_ai
    + email_text_linkedin
    + email_text_address
    + email_text_phone
    + disclaimer_text
    + url_text
  )

  subject = f"Lodginia – Ergebnisse für: {bookingdata}"

  anvil.email.send(
    to=user_email,
    from_address="noreply@lodginia.com",
    from_name="Lodginia.com",
    subject=subject,
    html=html_body,
  )
  print("E-Mail versendet:", user_email, reservation_id)
  return True

@anvil.server.callable
def delete_bookings_by_email_old(email):
    matching_rows = app_tables.bookings.search(email=email)
    deleted_count = 0    
    # Lösche jede gefundene Zeile
    for row in matching_rows:
        row.delete()
        deleted_count += 1
    print ("Buchungen von ",email," gelöscht. Anzahl: ",deleted_count)
    return deleted_count

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
def send_email(user_email,email_text):
  anvil.email.send(
      to=user_email,
      from_address="noreply@lodginia.com",  # Vollständige E-Mail-Adresse
      from_name="Lodginia.com",
      subject="Lodginia.com Ergebnisse",
      html=email_text
    )

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
def get_dashboard_data_dict():
  user = anvil.users.get_user()

  if not user:
    return {
      'bookings': [],
      'has_subscription': False,
      'server_data_last_update': None
    }

    # Bestimme Apartment-Limit basierend auf Subscription
  apartment_limit = 10 if user.get('subscription') == 'Pro-Subscription' else 3

  # Fetch alle Bookings mit optimiertem fetch_only
  all_bookings = get_bookings_from_supabase(user['email'])
  
  # Gruppiere und verarbeite Bookings in einem Durchgang
  apartments = {}
  for booking in all_bookings:
    apt = booking.get('apartment')
    apt_id = apt['id'] if isinstance(apt, dict) and 'id' in apt else apt

    if apt_id not in apartments:
      apartments[apt_id] = []
    apartments[apt_id].append(booking)

    # Sortiere Apartments nach frühestem Ankunftsdatum
  def earliest_arrival(booking_list):
    arrivals = [b.get('arrival') for b in booking_list if b.get('arrival')]
    return min(arrivals) if arrivals else datetime.max.replace(tzinfo=timezone.utc)

  sorted_apartment_ids = sorted(
    apartments.keys(), 
    key=lambda aid: earliest_arrival(apartments[aid])
  )[:apartment_limit]

  # Sammle und serialisiere Bookings in einem Schritt
  serialized_bookings = []
  for apt_id in sorted_apartment_ids:
    for booking in apartments[apt_id]:
      apt = booking.get('apartment')
      apt_id_final = apt['id'] if isinstance(apt, dict) and 'id' in apt else apt

      serialized_bookings.append({
        'guestname': booking.get('guestname'),
        'arrival': booking.get('arrival') if booking.get('arrival') else None,
       #'arrival': booking.get('arrival').isoformat() if booking.get('arrival') else None,
        'departure': booking.get('departure') if booking.get('departure') else None,
        'created_at': booking.get('created_at') if booking.get('created_at') else None,
        'apartment': apt_id_final,
        'channel_name': booking.get('channel_name'),
        'screener_google_linkedin': booking.get('screener_google_linkedin'),
        'address_street': booking.get('address_street'),
        'address_postalcode': booking.get('address_postalcode'),
        'address_city': booking.get('address_city'),
        'screener_address_check': booking.get('screener_address_check'),
        'screener_openai_job': booking.get('screener_openai_job'),
        'phone': booking.get('phone'),
        'screener_phone_check': booking.get('screener_phone_check'),
        'guest_email': booking.get('guest_email'),
        'screener_disposable_email': booking.get('screener_disposable_email'),        
        'adults': booking.get('adults'),
        'children': booking.get('children'),
        'language': booking.get('language'),
        'type': booking.get('type'),
        'price': booking.get('price'),
        'prepayment': booking.get('prepayment'),
        'deposit': booking.get('deposit'),
        'commission_included': booking.get('commission_included'),
        'price_paid': booking.get('price_paid'),
        'prepayment_paid': booking.get('prepayment_paid'),
        'deposit_paid': booking.get('deposit_paid'),
        'guest_count': booking.get('guest_count'),
        'revenue': booking.get('revenue'),
      })
  
    # Sortiere nach Ankunftsdatum
  serialized_bookings.sort(key=lambda b: b.get('arrival') or "")

  # Subscription-Status bestimmen
  has_subscription = user.get('subscription') in ['Subscription', 'Pro-Subscription', 'Canceled']

  if not has_subscription:
    signed_up_date = user.get('signed_up')
    if signed_up_date:
      trial_end = signed_up_date + timedelta(days=5)
      now_utc = datetime.now(timezone.utc)
      has_subscription = now_utc <= trial_end

  return {
    'bookings': serialized_bookings,
    'has_subscription': has_subscription,
    'server_data_last_update': user.get('server_data_last_update')
  }

@anvil.server.callable
def get_bookings_from_supabase(email):
  return (
    supabase.table("bookings")
      .select("*")
      .eq("email", email)
      .execute()
      .data
  )

@anvil.server.callable
def call_server_wake_up():
  anvil.server.launch_background_task('server_wake_up')
  pass

@anvil.server.background_task
def server_wake_up():
  result= 1+1
  return result