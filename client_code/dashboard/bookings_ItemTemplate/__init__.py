from ._anvil_designer import bookings_ItemTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class bookings_ItemTemplate(bookings_ItemTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.guestname_text_box.text=self.item['guestname']
    self.arrival_text_box.text=self.item['arrival']
    self.departure_text_box.text=self.item['departure']
    self.channel_name_text_box.text=self.item['channel_name']

    # Any code you write here will run before the form opens.
