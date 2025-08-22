# bookings.py

from ._anvil_designer import bookingsTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

# --- persistence: module-level single instance ---
_PERSISTENT_INSTANCE = None

def _get_persistent():
  global _PERSISTENT_INSTANCE
  if _PERSISTENT_INSTANCE is None:
    _PERSISTENT_INSTANCE = bookings()
  return _PERSISTENT_INSTANCE
# -------------------------------------------------

class bookings(bookingsTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self._initialized = False
    self._iframe_added = False
    self._one_time_init()

  def _one_time_init(self):
    if self._initialized:
      return

    user = users.get_user()
    if user:
      print('User Logged in: ', user.get('email'))

    user_has_subscription = anvil.server.call('get_user_has_subscription')
    self.looker_flow_panel.visible = False

    # Reset visibilities
    self.pms_need_to_connect_text.visible = False
    self.channel_manager_connect_button.visible = False
    self.dashboard_upgrade_needed_text.visible = False
    self.dashboard_upgrade_button.visible = False

    if user and user.get('smoobu_api_key') is None:
      self.pms_need_to_connect_text.visible = True
      self.chanel_manager_connect_button.visible = True
    else:
      if not user_has_subscription:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True

    if user_has_subscription and user and user.get('smoobu_api_key') is not None:
      self.looker_flow_panel.visible = True
      supabase_key = user.get('supabase_key')
      if not self._iframe_added:
        self.init_iframe(supabase_key)
        self._iframe_added = True

    self._initialized = True

  def init_iframe(self, supabase_key):
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_9euf3853td"
    params = {"supabase_key_url": supabase_key or ""}
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"
    print(iframe_url)

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })
    iframe.appendTo(get_dom_node(self.looker_flow_panel))

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')


# --- Register a form loader so open_form('bookings') uses the persistent instance ---
try:
  # Available in runtime; allows overriding how a form name is resolved
  anvil.app.register_form('bookings', _get_persistent)
  print("yes")
except Exception as e:
  # In IDE design-time or older runtimes, registration might not exist; ignore
  print("Form loader registration skipped:", e)
# -----------------------------------------------------------------------------------
