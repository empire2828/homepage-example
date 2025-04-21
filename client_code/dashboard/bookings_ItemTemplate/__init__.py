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
        # Aktuellen Benutzer abrufen
      self.init_components(**properties)
      self.guestname_text_box.text=self.item['guestname']
      self.arrival_text_box.text=self.item['arrival']
      self.departure_text_box.text=self.item['departure']
      self.channel_name_text_box.text=self.item['channel_name']
      self.google_linkedin_text_box.text=self.item['screener_google_linkedin']
      self.street_text_box.text=self.item['address_street']
      self.postal_code_text_box.text=self.item['address_postalcode']
      self.city_text_box.text=self.item['address_city']
      self.address_check_box.checked=self.item['screener_address_check']
      self.screener_open_ai_text.text=self.item['screener_openai_job']
      self.phone_text_box.text=self.item['phone']
      self.phone_check_box.checked=self.item['screener_phone_check']
      self.adults_text_box.text=self.item('adults')
      self.children_text_box.text=self.item('children')

    # Any code you write here will run before the form opens.
