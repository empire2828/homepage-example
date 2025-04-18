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
from tester import test_email

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
    email_text_ai = "OpenAI:<br>" + openai_job + "<br><br>"
  
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
  bookingdata = guestname+" "+arrival+" - "+departure 

  intro_text="Hier kommen die Guestscreener Ergebnisse für die neue Buchung: "+ bookingdata+ "<br><br><br>"
  
  email_text = intro_text+ email_text_ai + email_text_linkedin + email_text_address + email_text_phone
  print("send_email:", user_email, reservation_id, email_text)
  try:
    #send_email(user_email,email_text)
    anvil.email.send(
      to=user_email,
      from_address="noreply@guestscreener.com",  # Vollständige E-Mail-Adresse
      from_name="Guestscreener.com",
      subject="Guestscreener.com Ergebnisse",
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
def server_wake_up():
  anvil.server.launch_background_task('server_wake_up_background')
  pass

@anvil.server.background_task
def server_wake_up_background():
  print('Server woke up')

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