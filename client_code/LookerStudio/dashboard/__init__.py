from ._anvil_designer import dashboardTemplate
from anvil import *
from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

# Globaler Cache für iFrames
_iframe_cache = {}

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    user = users.get_user()
    print('User Logged in: ', user['email'])

    user_has_subscription = anvil.server.call('get_user_has_subscription')
    self.looker_flow_panel.visible = False

    if user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.chanel_manager_connect_button.visible = True
    else:
      if user_has_subscription is False:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True
        self.pms_need_to_connect_text.visible = False
        self.chanel_manager_connect_button.visible = False

    if user_has_subscription and user['smoobu_api_key'] is not None:
      self.looker_flow_panel.visible = True
      supabase_key = user['supabase_key']
      self.init_iframe(supabase_key)

  # Neu mit Cache
  def init_iframe(self, supabase_key):
    cache_key = f"looker_iframe_{supabase_key}"

    # Prüfen, ob iframe bereits im Cache ist
    if cache_key in _iframe_cache:
      print("🚀 Lade iframe aus Cache")
      # Panel bereinigen, altes entfernen
      get_dom_node(self.looker_flow_panel).innerHTML = ""
      # Vorhandenes iframe-Objekt erneut anhängen
      _iframe_cache[cache_key].appendTo(get_dom_node(self.looker_flow_panel))
      return

    # Iframe zum ersten Mal laden
    print("🌐 Lade iframe neu")
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    params = {"supabase_key_url": supabase_key}    
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })

    # ins Panel anhängen
    iframe.appendTo(get_dom_node(self.looker_flow_panel))

    # im Cache speichern
    _iframe_cache[cache_key] = iframe

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
