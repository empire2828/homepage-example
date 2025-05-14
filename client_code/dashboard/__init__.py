from ._anvil_designer import dashboardTemplate
from anvil import *
import anvil.facebook.auth
#import anvil.google.auth
#import anvil.tables as tables
#import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import users
import anvil.server
#from anvil_extras import routing
from anvil_extras.storage import local_storage
import time
from datetime import datetime, timedelta
#, timezone

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
  def form_show(self, **event_args):
    print("dashboard form show sart:", time.strftime("%H:%M:%S"))
    print("server call start:", time.strftime("%H:%M:%S"))
    self.layout.reset_links()
    user = users.get_user()
    dashboard_data = local_storage.get('dashboard_data')
    
    cache_too_old = False
    if dashboard_data:      
      last_login =  user['last_login'].replace(tzinfo=None)
      now = datetime.now()
      if now - last_login > timedelta(days=3):
        cache_too_old = True
        print('Cache too old', last_login,now)
    else:
      cache_too_old = True

    user_row = app_tables.users.get(email=user['email'])
    local_storage_update_needed = user_row['local_storage_update_needed'] 
    
    if not dashboard_data or cache_too_old or local_storage_update_needed:
      dashboard_data = anvil.server.call('get_dashboard_data_dict')
      local_storage['dashboard_data'] = dashboard_data
      user_row['local_storage_update_needed'] = False
    print("server call end:", time.strftime("%H:%M:%S"))    
    user_has_subscription= dashboard_data['has_subscription']

    if user_has_subscription:
      print("repeating panel start:", time.strftime("%H:%M:%S"))
      panel_data = dashboard_data['bookings']
      self.bookings_repeating_panel.items = panel_data
      print("repeating panel end:", time.strftime("%H:%M:%S"))
      
    if user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.refresh_button.visible = False
      self.resync_smoobu_button.visible = False
      self.chanel_manager_connect_button.visible = True
    else:
      if user_has_subscription is False:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True
        self.pms_need_to_connect_text.visible = False
        self.refresh_button.visible = False
        self.resync_smoobu_button.visible = False
        self.chanel_manager_connect_button.visible = False
        self.bookings_repeating_panel.visible = False
        
    print("dashboard form show end:", time.strftime("%H:%M:%S"))
  
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
    if user['smoobu_api_key'] is not None:
      alert("Hintergrund- Synchronisation wird gestartet. Das dauert ca. 10 Minuten.")
      anvil.server.call_s('delete_bookings_by_email',anvil.users.get_user()['email'])
      anvil.server.call_s('launch_sync_smoobu')
      anvil.server.call_s('launch_get_bookings_risk')
      self.init_components()
    pass

  def refresh_button_click(self, **event_args):
    local_storage['dashboard_data_last_login'] = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
    self.form_show()
    pass

  def chanel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def dashboard_upgrade_button_click(self, **event_args):    
    try:
      user = anvil.users.get_user()
      if not user:
        alert('Kein Benutzer angemeldet')
        return

      subscription = user.get('subscription')
      apartment_count = user.get('apartment_count', 0) or 1

      if subscription != 'Subscription' and apartment_count < 4:
        open_form('StripePricing')
      elif subscription != 'Pro-Subscription' and apartment_count > 3:
        open_form('StripePricing_pro')
      else:
        alert('Abo bereits vorhanden.')
    except Exception as e:
      alert(f'Ein Fehler ist aufgetreten: {e}')
  pass
  #identisch zu pflegen in Layout!


  
