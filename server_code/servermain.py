import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import google_linkedin
import address_check

@anvil.server.callable
def launch_get_bookings_risk():
  get_bookings_risk()
  pass

@anvil.server.background_task
def get_bookings_risk():
    bookings = app_tables.bookings.search(email=anvil.users.get_user()['email'])
    for booking in bookings:
      
        #google_linkedin
        result = google_linkedin.google_linkedin(booking['guestname'], booking['address_city'])
        booking['screener_google_linkedin'] = result
      
        #address check
        street = booking['address_street'] if booking['address_street'] is not None else ""
        postal = booking['address_postalcode'] if booking['address_postalcode'] is not None else ""
        city = booking['address_city'] if booking['address_city'] is not None else ""
        address = " ".join(filter(None, [street, postal, city]))
        result = address_check.address_check(address)
        booking['screener_address_check'] = result if result is not None else 0

        
      
    return bookings

