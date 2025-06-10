import anvil.users
from anvil.tables import app_tables
import anvil.server
from screener import screener_open_ai, google_linkedin, address_check, phone_check, screener_email
import time
from datetime import datetime, date

@anvil.server.callable
def launch_get_bookings_risk():
  email = anvil.users.get_user()['email']
  anvil.server.launch_background_task('get_bookings_risk', email)
  pass

@anvil.server.background_task
def get_bookings_risk(email=None, booking_id=None):
  if booking_id:
    time.sleep(5)
    bookings = [app_tables.bookings.get(reservation_id=booking_id)]
    if not bookings[0]:
      return None
  elif email:
    time.sleep(30)
    bookings = app_tables.bookings.search(email=email)
    print('Anzahl Buchungen: ', len(bookings))
  else:
    return None

    # Filter: Only bookings with arrival date in the future
  today = date.today()
  future_bookings = []
  for booking in bookings:
    # Assume booking['arrival'] is a string in 'YYYY-MM-DD' format
    # Adjust the key if your column name is different
    arrival_str = booking.get('arrival')
    if arrival_str:
      try:
        arrival_date = datetime.strptime(arrival_str, '%Y-%m-%d').date()
        if arrival_date > today:
          future_bookings.append(booking)
      except Exception as e:
        print(f"Error parsing arrival date: {arrival_str} - {e}")

    # Now process only future_bookings
  for booking in future_bookings:
    # OpenAI Job-Prüfung
    result = None  # screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "job")
    booking['screener_openai_job'] = result if result is not None else ""

    # Google LinkedIn-Prüfung
    result = google_linkedin.google_linkedin(booking['guestname'], booking['address_city'])
    booking['screener_google_linkedin'] = result if result is not None else ""

    # Adressprüfung
    street = booking['address_street'] or ""
    postal = booking['address_postalcode'] or ""
    city = booking['address_city'] or ""
    address = " ".join(filter(None, [street, postal, city]))
    result = address_check.address_check(address)
    booking['screener_address_check'] = result if result is not None else False

    # Phone check
    phone = booking['phone']
    result = phone_check.phone_check(phone)
    booking['screener_phone_check'] = result if result is not None else False

    # eMail check
    email = booking['guest_email']
    result = screener_email.is_disposable_email(email)
    booking['screener_disposable_email'] = result if result is not None else False

    # Bei einer einzelnen Buchung geben wir nur diese zurück
  if booking_id and future_bookings:
    return future_bookings[0]

  return future_bookings
