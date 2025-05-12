from ._anvil_designer import dashboardTemplate
from anvil import *
#import anvil.google.auth
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
from anvil import users
import anvil.server
#from anvil_extras import routing
from anvil_extras.storage import local_storage
import time

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
  def form_show(self, **event_args):
    print("dashboard form show start:", time.strftime("%H:%M:%S"))

    # 1. Daten aus Local Storage holen mit Default-Wert
    dashboard_data = local_storage.get('dashboard_data', {})

    # 2. Validierung des Server-Responses
    if not dashboard_data or 'has_subscription' not in dashboard_data:
      print("server call start:", time.strftime("%H:%M:%S"))
      try:
        dashboard_data = anvil.server.call('get_dashboard_data') or {}
        local_storage['dashboard_data'] = dashboard_data
      except Exception as e:
        print("Server error:", e)
        dashboard_data = {}
        print("server call end:", time.strftime("%H:%M:%S"))

    # 3. Sichere Zugriffe mit get()-Methode
    user_has_subscription = dashboard_data.get('has_subscription')
    panel_data = dashboard_data.get('bookings', [])

    if user_has_subscription and panel_data:
      print("repeating panel start:", time.strftime("%H:%M:%S"))
      self.bookings_repeating_panel.items = panel_data
      print("repeating panel end:", time.strftime("%H:%M:%S"))

    # 4. Null-Check für User-Objekt
    user = users.get_user()
    if not user:
      return

    # 5. Sichere Zugriffe auf User-Attribute
    smoobu_key = user.get('smoobu_api_key')

    if not smoobu_key:
      self.pms_need_to_connect_text.visible = True
      self.refresh_button.visible = False
      self.resync_smoobu_button.visible = False
      self.chanel_manager_connect_button.visible = True
    else:
      if not user_has_subscription:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True
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


  
