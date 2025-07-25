from ._anvil_designer import ItemTemplate1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate1(ItemTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.message_text.content = str(self.item['message'])
    self.email_text.text=str(self.item['email'])
    self.created_at_text.text=str(self.item['created_at'])
    self.function_text.text=str(self.item['function'])
    self.id_text.text=str(self.item['id'])
    self.ref_id_text.text=str(self.item['ref_id'])