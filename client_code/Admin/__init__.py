from ._anvil_designer import AdminTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

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
         result = anvil.server.call('import_bookings_csv', csv_file)

          # Erfolgsmeldung anzeigen
        alert(f"Import erfolgreich: {result}")

        # Optional: Seite neu laden oder Tabelle aktualisieren
        # self.refresh_data_bindings()

      except Exception as e:
        alert(f"Fehler beim Import: {str(e)}")

  def navigation_link_1_click(self, **event_args):
    open_form('pivot')
    pass
