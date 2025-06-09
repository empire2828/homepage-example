import anvil.users
from anvil.tables import app_tables
import anvil.server
from screener import screener_open_ai, google_linkedin, address_check, phone_check, screener_email
import time

@anvil.server.callable
def launch_get_bookings_risk():
  email=anvil.users.get_user()['email']
  anvil.server.launch_background_task('get_bookings_risk',email)
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
        print('Anzahl Buchungen: ',len(bookings))
    else:
        return None
    
    for booking in bookings:
        # OpenAI Job-Prüfung
        #result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "job")
        # to save 10 cent per updating all bookings #################################################################
        result= None
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
        phone=booking['phone']
        result = phone_check.phone_check(phone)
        booking['screener_phone_check'] = result if result is not None else False

        # eMail check
        email=booking['guest_email']
        result = screener_email.is_not_disposable_email(email)
        booking['screener_email'] = result if result is not None else False
    
    # Bei einer einzelnen Buchung geben wir nur diese zurück
    if booking_id and bookings:
        return bookings[0]
    
    return bookings