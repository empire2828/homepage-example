import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
#import openai
import screener_open_ai
import google_linkedin
import address_check

@anvil.server.callable
def launch_get_bookings_risk():
  email=anvil.users.get_user()['email']
  anvil.server.launch_background_task('get_bookings_risk',email)
  pass

@anvil.server.background_task
def get_bookings_risk(email=None, booking_id=None):
    if booking_id:
        bookings = [app_tables.bookings.get(id=booking_id)]
        if not bookings[0]:
            return None
    elif email:
        bookings = app_tables.bookings.search(email=email)
    else:
        return None
    
    for booking in bookings:
        # OpenAI Job-Prüfung
        result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "job")
        booking['screener_openai_job'] = result
      
        # Google LinkedIn-Prüfung
        result = google_linkedin.google_linkedin(booking['guestname'], booking['address_city'])
        booking['screener_google_linkedin'] = result
      
        # Adressprüfung
        street = booking['address_street'] if booking['address_street'] is not None else ""
        postal = booking['address_postalcode'] if booking['address_postalcode'] is not None else ""
        city = booking['address_city'] if booking['address_city'] is not None else ""
        address = " ".join(filter(None, [street, postal, city]))
        result = address_check.address_check(address)
        booking['screener_address_check'] = result if result is not None else 0

        # OpenAI Alters-Prüfung
        result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "age")
        booking['screener_openai_age'] = result
    
    # Bei einer einzelnen Buchung geben wir nur diese zurück
    if booking_id and bookings:
        return bookings[0]
    
    return bookings

@anvil.server.callable
def send_result_email(user_email,reservation_id):
  booking = app_tables.bookings.get(reservation_id=reservation_id)
  email_text= booking['screener_openai_job']
  print("send_email:",user_email,reservation_id,email_text)
  anvil.email.send(
    to=user_email,
    from_address="noreply",
    from_name="Guestscreener.com",
    subject="Guestscreener.com Ergebnisse",
    html=email_text
)
  pass