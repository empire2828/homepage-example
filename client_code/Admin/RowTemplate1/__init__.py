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
      self.created_at_body.text = str(self.item.get('created_at', ''))
      print('#####',str(self.item.get('created_at', '')))
      self.message_body.text = str(self.item.get('message', ''))
      print('#####',str(self.item.get('message', '')))
      self.email_body.text = self.item.get('email', '')
      print('#####',str(self.item.get('email', '')))
      self.function_body.text = str(self.item.get('function', ''))
      print('#####',str(self.item.get('function', '')))
    except Exception as e:
      print("Fehler im RowTemplate:", e)
      print("Item:", self.item)