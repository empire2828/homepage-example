from ._anvil_designer import guestscreenTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class guestscreen(guestscreenTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    self.layout.reset_links()

  def guestscreen_button_click(self, **event_args):
    """Handle button click event."""
    # AI Name Check
    guest_full_name = self.first_name_text_box.text + " " + self.family_name_text_box.text
    city = self.city_text_box.text
    
    # Perform AI checks
    aicheckResult_job = anvil.server.call('open_ai', guest_full_name, city, "job")
    self.AI_result_text_area.text = aicheckResult_job
    
    # Address Check
    address = self.street_text_box.text + " " + self.zip_text_box.text + " " + self.city_text_box.text
    address_check_result = anvil.server.call('address_check', address)
    print(address_check_result)
    if address_check_result:
      self.address_check_box.checked = address_check_result
    
    # LinkedIn Check
    linkedin_check_result = anvil.server.call('google_linkedin', guest_full_name, city)
    self.linkedin_check_text_box.text = linkedin_check_result
    
    # Additional AI Check for Age
    aicheckResult_age = anvil.server.call('open_ai', guest_full_name, city, "age")
    self.age_check_text_box.text = aicheckResult_age