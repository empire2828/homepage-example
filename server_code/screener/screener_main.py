import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from screener import screener_open_ai, google_linkedin, address_check, phone_check

@anvil.server.callable
def launch_get_bookings_risk():
  email=anvil.users.get_user()['email']
  anvil.server.launch_background_task('get_bookings_risk',email)
  pass

@anvil.server.background_task
def get_bookings_risk(email=None, booking_id=None):
    if booking_id:
        bookings = [app_tables.bookings.get(reservation_id=booking_id)]
        if not bookings[0]:
            return None
    elif email:
        bookings = app_tables.bookings.search(email=email)
    else:
        return None
    
    for booking in bookings:
        # OpenAI Job-Prüfung
        result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "job")
        print('AI result: ',result)
        booking['screener_openai_job'] = result
      
        # Google LinkedIn-Prüfung
        result = google_linkedin.google_linkedin(booking['guestname'], booking['address_city'])
        print('linkedin_result: ',result)
        booking['screener_google_linkedin'] = result
      
        # Adressprüfung
        street = booking['address_street'] or ""
        postal = booking['address_postalcode'] or ""
        city = booking['address_city'] or ""
        address = " ".join(filter(None, [street, postal, city]))
        result = address_check.address_check(address)
        print('address_check: ',result)
        booking['screener_address_check'] = result if result is not None else False

        # Phone check
        phone=booking['phone']
        result = phone_check.phone_check(phone)
        print('phone_check:',result)
        booking['screener_phone_check'] = result if result is not None else False

        # OpenAI Alters-Prüfung
        # result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "age")
        # booking['screener_openai_age'] = result
    
    # Bei einer einzelnen Buchung geben wir nur diese zurück
    if booking_id and bookings:
        return bookings[0]
    
    return bookings

