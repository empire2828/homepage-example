from ._anvil_designer import dashboardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil_extras import routing
from users import get_user_has_subscription

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    filtered_data = app_tables.bookings.search(email=anvil.users.get_user()['email'])
    self.bookings_repeating_panel.items = filtered_data
    
  def form_show(self, **event_args):
    self.layout.reset_links()
    user = users.get_user()
    #if get_user_has_subscription:
    if user['pms_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.refresh_button.visible = False
      self.resync_smoobu_button.visible = False
      self.chanel_manager_connect_button.visible = True

  def form_refreshing_data_bindings(self, **event_args):
    """This method is called when refresh_data_bindings is called"""
    pass

  def sync_smoobu_button_click(self, **event_args):
    anvil.server.call_s('launch_sync_smoobu')
    anvil.server.call_s('launch_get_bookings_risk')
    alert("Sync in process.")
    pass

  def resync_smoobu_button_click(self, **event_args):
    user = users.get_user()
    if user['pms_api_key'] is not None:
      alert("Hintergrund- Synchronisation wird gestartet. Das dauert ca. 10 Minuten.")
      anvil.server.call_s('delete_bookings_by_email',anvil.users.get_user()['email'])
      anvil.server.call_s('launch_sync_smoobu')
      anvil.server.call_s('launch_get_bookings_risk')
      self.init_components()
    pass

  def refresh_button_click(self, **event_args):
    self.__init__()
    pass

  def chanel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass



  
