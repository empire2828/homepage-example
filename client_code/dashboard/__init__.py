from ._anvil_designer import dashboardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    filtered_data = app_tables.bookings.search(email=anvil.users.get_user()['email'])
    self.bookings_repeating_panel.items = filtered_data
    
  def form_show(self, **event_args):
    self.layout.reset_links()

  def form_refreshing_data_bindings(self, **event_args):
    """This method is called when refresh_data_bindings is called"""
    pass

  def sync_smoobu_button_click(self, **event_args):
    anvil.server.call_s('launch_sync_smoobu')
    anvil.server.call_s('launch_get_bookings_risk')
    alert("Sync in process.")
    pass

  def resync_smoobu_button_click(self, **event_args):
    alert("Hintergrund- Synchronisation wird gestartet. Das dauert ca. 10 Minuten.")
    anvil.server.call_s('launch_sync_smoobu')
    anvil.server.call_s('launch_get_bookings_risk')
    pass

  def refresh_button_click(self, **event_args):
    self.__init__()
    pass


  