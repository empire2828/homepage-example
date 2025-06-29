from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
import time
from datetime import datetime, timedelta
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    user = users.get_user()
    print('User Logged in: ',user['email'])

    user_has_subscription= anvil.server.call('get_user_has_subscription')
    self.looker_flow_panel.visible = False

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
        self.chanel_manager_connect_button.visible = False

    if user_has_subscription and user['smoobu_api_key'] is not None:
      self.looker_flow_panel.visible = True
      email= user['email']
      self.init_iframe(email)
    else: 
      pass

  def init_iframe(self, supabase_key):
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    #https://lookerstudio.google.com/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de
    params = {"supabase_key": supabase_key}

    # URL mit Parameter kodieren
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"
    print (iframe_url)

    # iFrame erstellen und einbinden
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      #"height": "100%",
      "height": "1400px",
      "frameborder": "0"
    })
    #iframe = jQuery("<iframe class='anvil-role-looker-iframe flex-column-fill'>").attr("src", iframe_url)
    iframe.appendTo(get_dom_node(self.looker_flow_panel))# Any code you write here will run before the form opens.

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
    pass

  def chanel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass
