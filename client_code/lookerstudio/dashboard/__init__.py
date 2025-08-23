from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil import users
import anvil.server, json
from anvil.js.window import jQuery
from anvil.js import get_dom_node

class dashboard(dashboardTemplate):
  def __init__(self, **props):
    self.init_components(**props)
    self._iframe = None
    self._iframe_initialized = False
    self._can_show = False

    user = users.get_user()
    has_sub = anvil.server.call('get_user_has_subscription')
    if has_sub and user['smoobu_api_key'] is not None:
      self._can_show = True

  def on_first_show(self):
    if self._iframe_initialized or not self._can_show:
      return
    self._iframe_initialized = True  # ensures one-time init

    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    params = {"supabase_key_url": users.get_user()['supabase_key']}
    from anvil.js.window import encodeURIComponent
    iframe_url = f"{base_url}?params={encodeURIComponent(json.dumps(params))}"

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })
    iframe.appendTo(get_dom_node(self.looker_flow_panel))
    self._iframe = iframe

