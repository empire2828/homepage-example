import anvil.email
import anvil.users
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import time
from datetime import datetime, timedelta, timezone
from . import routes # noqa: F401

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

  intro_text="Hier kommen die Guestscreener Ergebnisse für die neue Buchung: "+ bookingdata+ "<br><br><br>"
  disclaimer_text="Die Ergebnisse können insbesondere bei häufig vorkommenen Namen falsch sein."+"<br><br><br>"
  url_text="guestscreener.com"
  
  email_text = intro_text+ email_text_ai + email_text_linkedin + email_text_address + email_text_phone+ disclaimer_text+ url_text
  subject="Guestscreener- Ergebnisse für: "+ bookingdata
  print("send_email:", user_email, reservation_id, email_text)
  try:
    anvil.email.send(
      to=user_email,
      from_address="noreply@guestscreener.com",  # Vollständige E-Mail-Adresse
      from_name="Guestscreener.com",
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
      from_address="noreply@guestscreener.com",  # Vollständige E-Mail-Adresse
      from_name="Guestscreener.com",
      subject="Guestscreener.com Ergebnisse",
      html=email_text
    )

@anvil.server.callable
def delete_old_bookings():
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=14)
    matching_rows = app_tables.bookings.search(departure=lambda d: d <= cutoff_date)
    deleted_count = 0
    for row in matching_rows:
        row.delete()
        deleted_count += 1
    print(f"Buchungen gelöscht, deren Abreisedatum 14 Tage oder mehr zurückliegt. Anzahl: {deleted_count}")
    return deleted_count

@anvil.server.callable
def send_registration_notification(user_email):
  anvil.email.send(
    to="dirk.klemer@gmail.com",  # Deine eigene Adresse
    subject="Neuer Benutzer registriert für Guestscreener.com",
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
      subject="Neue Supportanfragen vom Guestscreener.com",
      text=text + "\n\n" + str(email),
      attachments=attachments
    )
    print("send_email_to_support: success", email, text)
  except Exception as e:
    print("send_email_to_support: ERROR", e)

@anvil.server.callable
def get_dashboard_data_dict():
  user = anvil.users.get_user()
  filtered_bookings = []
  has_subscription = False
  server_data_last_update = None

  if user:
    # Determine apartment limit based on subscription
    if user.get('subscription') == 'Pro-Subscription':
      apartment_limit = 10
    else:
      apartment_limit = 3

      # Fetch all bookings for the user, fetch all relevant fields
    all_bookings = app_tables.bookings.search(
      q.fetch_only(
        "guestname", "arrival", "departure", "apartment",
        "channel_name", "screener_google_linkedin", "address_street",
        "address_postalcode", "address_city", "screener_address_check",
        "screener_openai_job", "phone", "screener_phone_check",
        "adults", "children"
      ),
      email=user['email']
    )

    # Group bookings by apartment
    apartments = {}
    for b in all_bookings:
        apt = b.get('apartment')
        # Handle both reference and string/int IDs
        apt_id = apt['id'] if isinstance(apt, dict) and 'id' in apt else apt
        if apt_id not in apartments:
            apartments[apt_id] = []
        apartments[apt_id].append(b)

        # Sort apartments by earliest arrival date
        def earliest_arrival(booking_list):
            arrivals = [bk.get('arrival') for bk in booking_list if bk.get('arrival')]
            return min(arrivals) if arrivals else datetime.max.replace(tzinfo=timezone.utc)
        sorted_apartment_ids = sorted(apartments.keys(), key=lambda aid: earliest_arrival(apartments[aid]))

        # Select up to apartment_limit apartments
        selected_apartment_ids = sorted_apartment_ids[:apartment_limit]

        # Collect bookings from selected apartments only
        filtered_bookings = []
        for apt_id in selected_apartment_ids:
            filtered_bookings.extend(apartments[apt_id])

        # Serialize and sort bookings by arrival date
        serialized_bookings = []
        for b in filtered_bookings:
            apt = b.get('apartment')
            apt_id = apt['id'] if isinstance(apt, dict) and 'id' in apt else apt
            serialized_bookings.append({
                'guestname': b.get('guestname'),
                'arrival': b.get('arrival').isoformat() if b.get('arrival') else None,
                'departure': b.get('departure').isoformat() if b.get('departure') else None,
                'apartment': apt_id,
                'channel_name': b.get('channel_name'),
                'screener_google_linkedin': b.get('screener_google_linkedin'),
                'address_street': b.get('address_street'),
                'address_postalcode': b.get('address_postalcode'),
                'address_city': b.get('address_city'),
                'screener_address_check': b.get('screener_address_check'),
                'screener_openai_job': b.get('screener_openai_job'),
                'phone': b.get('phone'),
                'screener_phone_check': b.get('screener_phone_check'),
                'adults': b.get('adults'),
                'children': b.get('children')
            })

        serialized_bookings.sort(key=lambda b: b.get('arrival') or "")

        # Subscription logic
        if user.get('subscription') in ['Subscription', 'Pro-Subscription', 'Canceled']:
            has_subscription = True
        else:
            signed_up_date = user.get('signed_up')
            if signed_up_date:
                trial_end = signed_up_date + timedelta(days=5)
                now_utc = datetime.now(timezone.utc)
                has_subscription = now_utc <= trial_end

        server_data_last_update = user.get('server_data_last_update')

    return {
        'bookings': serialized_bookings,
        'has_subscription': has_subscription,
        'server_data_last_update': server_data_last_update
    }

@anvil.server.callable
def call_server_wake_up():
  anvil.server.launch_background_task('server_wake_up')
  pass

@anvil.server.background_task
def server_wake_up():
  result= 1+1
  return result