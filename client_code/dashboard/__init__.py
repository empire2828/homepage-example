from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    user = users.get_user()
    if user and 'supabase_key' in user:
      supabase_key= user['supabase_key']
      self.init_iframe(supabase_key)
    else: 
      pass

  def init_iframe(self, supabase_key):
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    #https://lookerstudio.google.com/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de
    params = {"supabase_key_url": supabase_key}    

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
