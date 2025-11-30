from ._anvil_designer import home_deTemplate
from anvil import *
import anvil.server
import anvil.users
from ... import globals
#from anvil import js

class home_de(home_deTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.set_event_handler("show", self.form_show)

  def form_show(self, **event_args):
    # Wird aufgerufen, wenn die Form angezeigt wird
    self.headline_1.scroll_into_view(smooth=True)

  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:     
      # init variables
      globals.current_user = user
      globals.request_count = 0
      globals.user_has_subscription= False
      anvil.server.call_s("create_supabase_key")

      open_form('channel_manager_connect')

      anvil.server.call_s("send_registration_notification", user["email"])

  def impressum_link_click(self, **event_args):
    open_form("home.impressum")
    pass
    
  def pricing_link_click(self, **event_args):
    self.pricing_label.scroll_into_view()
    pass

  def data_protection_link_click(self, **event_args):
    open_form("home.data_protection")
    pass

### beim Ändern nicht die englische Version vergessen!!
