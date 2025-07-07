from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    try:
      self.timestamp_body.text = self.item['created_at']
      self.message_body.text = self.item['message']
      self.email_body.text = self.item['email']
      self.function_body.text = self.item['function']
    except Exception as e:
      print("Fehler im RowTemplate:", e)
      print("Item:", self.item)