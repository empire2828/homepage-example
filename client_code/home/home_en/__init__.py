from ._anvil_designer import home_enTemplate
from anvil import *
#from routing import router
#import m3.components as m3
import anvil.server
import anvil.users
#import anvil.js
from ... import globals

class home_en(home_enTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
  
  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
      anvil.server.call('create_supabase_key')
      anvil.server.call('send_registration_notification', user['email'])
      # Layout Template öffnen
      globals.current_user = user
      globals.request_count = 0
      globals.user_has_subscription= False
      layout_form = open_form('layout_template')
      # Dashboard automatisch laden
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True   
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
    pass
  
  def impressum_link_click(self, **event_args):
    open_form('home.impressum')
    pass
  
  def pricing_link_click(self, **event_args):
    self.pricing_label.scroll_into_view()
    pass

  def data_protection_link_click(self, **event_args):
    open_form('home.data_protection')
    pass



