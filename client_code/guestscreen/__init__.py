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
    self.layout.guestscreen.role = 'selected'

   #ai name check
   guest_full_name = self.first_name_textbox.text + " " + self.family_name_textbox.text
   city = self.city_textbox.text
   aicheckResult= anvil.server.call('open_ai',guest_full_name,city,"job")
   self.CheckGuests_text.text= aicheckResult
   # address check
   #address = self.complete_address_textbox.text
   #address_check_result = anvil.server.call('address_check', address)
   #self.address_check_result_textbox.text= address_check_result
   #guest_full_name = self.first_name_textbox.text + " " + self.family_name_textbox.text
   # linkedin check
   #linkedin_check_result = anvil.server.call('google_linkedin', guest_full_name, city)
   #self.linkedin_textbox.text= linkedin_check_result
   #ai age check
   #aicheckResult= anvil.server.call('open_ai',guest_full_name,city, "age")
   #self.age_textbox.text= aicheckResult