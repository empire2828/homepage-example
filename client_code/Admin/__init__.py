from ._anvil_designer import AdminTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import time

class Admin(AdminTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def admin_file_loader_change(self, file, **event_args):
    """Diese Methode wird aufgerufen, wenn eine Datei hochgeladen wird"""
    if file:
      try:
        csv_file = file

        # Dateitype überprüfen
        if not (csv_file.name.endswith('.csv') or csv_file.content_type == 'text/csv'):
          alert("Bitte laden Sie eine CSV-Datei hoch.")
          return

          # Loading-Indikator anzeigen
        with anvil.server.no_loading_indicator:
         result = anvil.server.call('import_csv', csv_file)

          # Erfolgsmeldung anzeigen
        alert(f"Import erfolgreich: {result}")

        # Optional: Seite neu laden oder Tabelle aktualisieren
        # self.refresh_data_bindings()

      except Exception as e:
        alert(f"Fehler beim Import: {str(e)}")

  def delete_bq_data_button_click(self, **event_args):
    email = self.email_input_prompt.text
    if not email:
      alert("Kein Nutzer angemeldet oder E-Mail nicht verfügbar.")
      return
  
    try:
      result = anvil.server.call('delete_userparameter_in_bigquery', email)
      if isinstance(result, dict) and 'count' in result:
        alert(f"{result['count']} Datensätze mit der E-Mail {email} wurden gelöscht.")
      else:
        alert(f"Parameter-Daten für {email} wurden gelöscht.")
    except Exception as e:
      alert(f"Fehler beim Löschen: {e}")
  
    try:
      result = anvil.server.call('delete_bookings_by_email', email)
      if isinstance(result, dict) and 'count' in result:
        alert(f"{result['count']} Buchungen mit der E-Mail {email} wurden gelöscht.")
    except Exception as e:
      alert(f"Fehler beim Parameter löschen in Bigquery: {e}")
  
    try:
      user_deleted = anvil.server.call('delete_user_from_users_table', email)
      if user_deleted:
        alert(f"User {email} aus der Users-Tabelle gelöscht.")
    except Exception as e:
      alert(f"Fehler beim User löschen in Bigquery: {e}")

  def log_filter_text_box_pressed_enter(self, **event_args):
    # Logs vom Server holen
    self.filtered_logs = anvil.server.call('search_logs', self.log_filter_text_box.text)
    self.logs_repeating_panel.items = self.filtered_logs

  def sync_all_smoobu_users_button_click(self, **event_args):
    results= anvil.server.call('sync_smoobu_for_all_smoobu_subscribers')
    pass


