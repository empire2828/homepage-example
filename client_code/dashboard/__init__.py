from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil_extras.storage import local_storage
import time
from datetime import datetime, timedelta

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
  def form_show(self, **event_args):
    print("dashboard form show sart:", time.strftime("%H:%M:%S"))
    print("server call start:", time.strftime("%H:%M:%S"))
    user = users.get_user()
    dashboard_data = local_storage.get('dashboard_data')
    
    cache_too_old = False
    if dashboard_data:      
      last_login =  user['last_login'].replace(tzinfo=None)
      now = datetime.now()
      if now - last_login > timedelta(days=7):
        cache_too_old = True
        print('Cache too old', last_login,now)
    else:
      cache_too_old = True

    local_storage_update_needed = True
    if user is not None and dashboard_data is not None:
      if ('server_data_last_update' in dashboard_data and
         user['server_data_last_update'] is not None and 
         dashboard_data['server_data_last_update'] is not None):
            if dashboard_data['server_data_last_update'] >= user['server_data_last_update']:
              local_storage_update_needed = False

    if dashboard_data is not None:
      local_date = dashboard_data.get('server_data_last_update')
      if local_date is not None:
        print('local_date', local_date)

    if user is not None:
      server_date = user.get('server_data_last_update')
      if server_date is not None:
        print('server_date', server_date)
   
    print('local_storage_update_needed: ',local_storage_update_needed)
    
    if not dashboard_data or cache_too_old or local_storage_update_needed:
      dashboard_data = anvil.server.call('get_dashboard_data_dict')
      local_storage['dashboard_data'] = dashboard_data
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
      result = alert(
        content="Hierdurch werden im Hintergrund alle Daten erneut synchronsiert. Dies ist normalerweise nicht notwendig, da neue Buchungen per API automatisiert empfangen werden. Die erneute Synchronisation dauert ca. 10 Minuten.",
        title="Re-synchronisation Starten?",
        buttons=[
          ("Ja", "YES"),
          ("Nein", "NO"),
        ]
      )
      if result == "YES":
        local_storage.clear()
        anvil.server.call_s('delete_bookings_by_email',anvil.users.get_user()['email'])
        anvil.server.call_s('launch_sync_smoobu')
        anvil.server.call_s('launch_get_bookings_risk')
        pass
      else:
      # Code ausführen, wenn Benutzer Nein wählt oder das Popup schließt
        pass

  def refresh_button_click(self, **event_args):
    local_storage.clear()
    self.bookings_repeating_panel.items = []
    self.form_show()
    self.refresh_data_bindings()
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


  
