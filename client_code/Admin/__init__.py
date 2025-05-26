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

  def admin_file_loader_change(self, files, **event_args):
    if files:
      csv_file = files[0]
      result = anvil.server.call('import_bookings_csv', csv_file.get_bytes())
      print(result)  # "X Zeilen importiert"
