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
def get_bookings_risk(email=None, reservation_id=None):
    # Entweder nach E-Mail oder nach Reservierungs-ID suchen
    if reservation_id is not None:
        # Suche nach einer spezifischen Reservierung
        bookings = [app_tables.bookings.get(reservation_id=reservation_id)]
        # Falls keine Reservierung gefunden wurde
        if bookings[0] is None:
            return []
    elif email is not None:
        # Suche nach allen Reservierungen für eine E-Mail
        bookings = app_tables.bookings.search(email=email)
    else:
        # Wenn weder E-Mail noch Reservierungs-ID angegeben wurden
        return []
    
    # Aktualisiere den Fortschritt im Task-Status
    anvil.server.task_state['total_bookings'] = len(bookings)
    anvil.server.task_state['processed_bookings'] = 0
    
    processed_bookings = []
    
    for booking in bookings:
        # Aktualisiere den Task-Status mit der aktuellen Reservierung
        anvil.server.task_state['current_booking'] = booking['reservation_id']
        
        # OpenAI Job-Prüfung
        result = screener_open_ai.screener_open_ai(booking['guestname'], booking['address_city'], "job")
        booking['screener_openai_job'] = result
        
        # Google/LinkedIn-Prüfung
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
        
        processed_bookings.append(booking)
        
        # Aktualisiere den Fortschritt
        anvil.server.task_state['processed_bookings'] += 1
    
    return processed_bookings


@anvil.server.callable
def send_email(user_email,email_text,email_subject,reservation_id):
  anvil.email.send(
    to=user_email,
    from_address="noreply",
    from_name="Guestscreener.com",
    subject=email_subject,
    html=email_text
)
  pass