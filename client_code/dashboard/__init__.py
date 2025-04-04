from ._anvil_designer import dashboardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #self.bookings_repeating_panel.items = app_tables.bookings.search()
    filtered_data = app_tables.bookings.search(email=anvil.users.get_user()['email'])
    self.bookings_repeating_panel.items = filtered_data
    
  def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    self.layout.reset_links()

  def form_refreshing_data_bindings(self, **event_args):
    """This method is called when refresh_data_bindings is called"""
    pass

  def sync_smoobu_button_click(self, **event_args):
    anvil.server.call('launch_sync_smoobu')
    anvil.server.call('launch_get_bookings_risk')
    alert("Sync in process.")
    pass


  