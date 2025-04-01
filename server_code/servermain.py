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

@anvil.server.callable
def get_bookings_risk():
    
  #google_linkedin
    bookings = app_tables.bookings.search(email=anvil.users.get_user()['email'])
    for booking in bookings:
        result = google_linkedin.google_linkedin(booking['guestname'], booking['address_city'])
        bookings['screener_google_linkedin'] = result
    return bookings

