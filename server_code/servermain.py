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
  time.sleep(60)
  try:
    booking = app_tables.bookings.get(reservation_id=reservation_id)
  except AttributeError:
    print("Keine Buchung gefunden",user_email, reservation_id)
    return False
  
 # OpenAI Ergebnisse
  openai_job = booking['screener_openai_job']
  if openai_job is None:
    email_text_ai = "OpenAI: Keine Ergebnisse<br>"
  else:
    email_text_ai = "OpenAI: " + openai_job + "<br><br>"
  
  # LinkedIn Ergebnisse
  linkedin_check = booking['screener_google_linkedin']
  if linkedin_check is None:
    email_text_linkedin = "LinkedIn: Keine Ergebnisse<br>"
  else:
    email_text_linkedin = "LinkedIn: " + linkedin_check + "<br><br>"
  
  # Adresscheck Ergebnisse
  address_check = booking['screener_address_check']
  if address_check is None:
    email_text_address = "Adresscheck: Keine Ergebnisse<br>"
  else:
    email_text_address = "Adresscheck: " + ("Erfolgreich" if address_check else "Fehlgeschlagen") + "<br><br>"

    # Phone check Ergebnisse
  phone_check = booking['screener_phone_check']
  if phone_check is None:
    email_text_phone = "Phone check: Keine Ergebnisse<br>"
  else:
    email_text_phone = "Phone check: " + ("Erfolgreich" if phone_check else "Fehlgeschlagen") + "<br><br>"

  #Buchungsdaten und Namen des Gastes
  guestname= booking['guestname'] or ""
  arrival= booking['arrival'] or ""
  departure= booking['departure'] or ""
  bookingdata = guestname + " " + str(arrival) + " - " + str(departure)

  intro_text="Hier kommen die Lodginia Ergebnisse für die neue Buchung: "+ bookingdata+ "<br><br><br>"
  disclaimer_text="Die Ergebnisse können insbesondere bei häufig vorkommenen Namen falsch sein."+"<br><br><br>"
  url_text="Lodginia.com"
  
  email_text = intro_text+ email_text_ai + email_text_linkedin + email_text_address + email_text_phone+ disclaimer_text+ url_text
  subject="Lodginia- Ergebnisse für: "+ bookingdata
  print("send_email:", user_email, reservation_id, email_text)
  try:
    anvil.email.send(
      to=user_email,
      from_address="noreply@lodginia.com",  # Vollständige E-Mail-Adresse
      from_name="Lodginia.com",
      subject=subject,
      html=email_text
    )
    print("email versendet: ",user_email,email_text)
    return True
  
  except anvil.email.SendFailure as e:
    print(f"Send-Fehler beim E-Mail-Versand: {str(e)}")
  except Exception as e:
    print(f"Allg.Fehler beim E-Mail-Versand: {str(e)}")
    return False

@anvil.server.callable
def delete_bookings_by_email(email):
    matching_rows = app_tables.bookings.search(email=email)
    deleted_count = 0    
    # Lösche jede gefundene Zeile
    for row in matching_rows:
        row.delete()
        deleted_count += 1
    print ("Buchungen von ",email," gelöscht. Anzahl: ",deleted_count)
    return deleted_count

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
        'arrival': booking.get('arrival').isoformat() if booking.get('arrival') else None,
        'departure': booking.get('departure').isoformat() if booking.get('departure') else None,
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
        'children': booking.get('children')
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

def get_bookings_from_supabase(email):
  response = supabase_client.from_('bookings').eq('email', email).execute()
  return response.data

@anvil.server.callable
def call_server_wake_up():
  anvil.server.launch_background_task('server_wake_up')
  pass

@anvil.server.background_task
def server_wake_up():
  result= 1+1
  return result