import anvil.facebook.auth
import anvil.email
#import anvil.secrets
#import anvil.google.auth, anvil.google.mail
import anvil.users
#import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import time
from datetime import datetime, timedelta
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
    #send_email(user_email,email_text)
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
def get_dashboard_data():
  print("server code start:", time.strftime("%H:%M:%S"))
  user = anvil.users.get_user()

  # Fetch bookings data
  bookings = app_tables.bookings.search(
    q.fetch_only(
      "guestname", "arrival", "departure", "apartment",
      "channel_name", "screener_google_linkedin", "address_street",
      "address_postalcode", "address_city", "screener_address_check",
      "screener_openai_job", "phone", "screener_phone_check",
      "adults", "children"
    ),
    email=user['email']
  )

  # Subscription check logic
  has_subscription = False
  if user:
    if user['subscription'] in ['Subscription', 'Pro-Subscription', 'Canceled']:
      has_subscription = True
    else:
      signed_up_date = user['signed_up']
      if signed_up_date:
        signed_up_aware = signed_up_date.replace
        trial_end = signed_up_aware + timedelta(days=5)
        now_utc = datetime.now
        has_subscription = now_utc <= trial_end
        
    print("server code end:", time.strftime("%H:%M:%S"))
    return {
      'bookings': list(bookings),
      'has_subscription': has_subscription
    }

@anvil.server.callable
def get_dashboard_data_dict():
  print("server code start:", time.strftime("%H:%M:%S"))
  user = anvil.users.get_user()

  # Initialisiere bookings als leere Liste für den Fall, dass kein User existiert
  bookings = []
  has_subscription = False

  if user:
    # Buchexistenz prüfen
    bookings = app_tables.bookings.search(
      q.fetch_only(
        "guestname", "arrival", "departure", "apartment",
        "channel_name", "screener_google_linkedin", "address_street",
        "address_postalcode", "address_city", "screener_address_check",
        "screener_openai_job", "phone", "screener_phone_check",
        "adults", "children"
      ),
      email=user['email']
    )

    # Serialisierung der Buchungen
    serialized_bookings = []
    for b in bookings:      
      serialized_bookings.append({
        'guestname': b['guestname'],
        'arrival': b['arrival'].isoformat() if b['arrival'] else None,
        'departure': b['departure'].isoformat() if b['departure'] else None,
        'apartment': b['apartment'] if isinstance(b['apartment'], str) else b['apartment']['id'],
        'channel_name': b['channel_name'],
        'screener_google_linkedin': b['screener_google_linkedin'],
        'address_street': b['address_street'],
        'address_postalcode': b['address_postalcode'],
        'address_city': b['address_city'],
        'screener_address_check': b['screener_address_check'],
        'screener_openai_job': b['screener_openai_job'],
        'phone': b['phone'],
        'screener_phone_check': b['screener_phone_check'],
        'adults': b['adults'],
        'children': b['children']
      })

      # Subscription-Logik korrigiert
      if user['subscription'] in ['Subscription', 'Pro-Subscription', 'Canceled']:
        has_subscription = True
      else:
        signed_up_date = user['signed_up']
        if signed_up_date:
          # Korrekte Zeitberechnung mit Zeitzone
          trial_end = signed_up_date + timedelta(days=5)
          now_utc = datetime.now
          has_subscription = now_utc <= trial_end

    print("server code end:", time.strftime("%H:%M:%S"))

  return {
    'bookings': serialized_bookings,  # Serialisierte Daten statt Row-Objekte
    'has_subscription': has_subscription
  }

@anvil.server.callable
def call_server_wake_up():
  anvil.server.launch_background_task('server_wake_up')
  pass

@anvil.server.background_task
def server_wake_up():
  result= 1+1
  return result

@anvil.server.callable
def get_local_storage():
  user_row = app_tables.users.get(email=user_email)
  local_storage_update_needed = user_row['local_storage_update_needed'] 