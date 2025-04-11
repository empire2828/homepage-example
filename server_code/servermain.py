import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import time

@anvil.server.callable
@anvil.server.background_task
def send_result_email(user_email, reservation_id):
  time.sleep(60)
  try:
    booking = app_tables.bookings.get(reservation_id=reservation_id)
  except AttributeError:
    print("Keine Buchung gefunden",user_email, reservation_id)
  
 # OpenAI Ergebnisse
  openai_job = booking['screener_openai_job']
  if openai_job is None:
    email_text_ai = "OpenAI: Keine Ergebnisse<br>"
  else:
    email_text_ai = "OpenAI:<br>" + openai_job + "<br><br>"
  
  # Adresscheck Ergebnisse
  address_check = booking['screener_address_check']
  if address_check is None:
    email_text_address = "Adresscheck: Keine Ergebnisse<br>"
  else:
    email_text_address = "Adresscheck: " + ("Erfolgreich" if address_check else "Fehlgeschlagen") + "<br><br>"
  
  # LinkedIn Ergebnisse
  linkedin_check = booking['screener_google_linkedin']
  if linkedin_check is None:
    email_text_linkedin = "LinkedIn: Keine Ergebnisse<br>"
  else:
    email_text_linkedin = "LinkedIn: " + linkedin_check + "<br><br>"
  
  email_text = email_text_ai + email_text_address + email_text_linkedin
  print("send_email:", user_email, reservation_id, email_text)
  anvil.email.send(
    to=user_email,
    from_address="noreply",
    from_name="Guestscreener.com",
    subject="Guestscreener.com Ergebnisse",
    html=email_text
  )

@anvil.server.callable
def server_wake_up():
  anvil.server.launch_background_task('server_wake_up_background')
  pass

@anvil.server.background_task
def server_wake_up_background():
  print('Server woke up')