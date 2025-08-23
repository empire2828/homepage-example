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
    self.init_components(**properties)
    self._iframe = None          # cache for the iframe element
    self._iframe_url = None      # cache for the url (optional, handy for debugging)

    user = users.get_user()
    print("User Logged in:", user['email'])

    user_has_subscription = anvil.server.call('get_user_has_subscription')
    self.looker_flow_panel.visible = False

    # UI states
    self.pms_need_to_connect_text.visible = user['smoobu_api_key'] is None
    self.channel_manager_connect_button.visible = user['smoobu_api_key'] is None

    need_upgrade = (user['smoobu_api_key'] is not None) and (not user_has_subscription)
    self.dashboard_upgrade_needed_text.visible = need_upgrade
    self.dashboard_upgrade_button.visible = need_upgrade

    # Only show Looker when allowed
    if user_has_subscription and user['smoobu_api_key'] is not None:
      self.looker_flow_panel.visible = True
      self._ensure_iframe(user['supabase_key'])

  def _ensure_iframe(self, supabase_key):
    # If iframe already exists, do nothing (prevents reload)
    if self._iframe is not None:
      print("iframe already exists")
      return

    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    params = {"supabase_key_url": supabase_key}
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"
    self._iframe_url = iframe_url
    print("Looker iFrame URL:", iframe_url)

    # Create once and append
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })
    iframe.appendTo(get_dom_node(self.looker_flow_panel))

    # Cache the element so it persists across show/hide and navigation
    self._iframe = iframe

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
