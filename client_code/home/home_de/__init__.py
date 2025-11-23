from ._anvil_designer import home_deTemplate
from anvil import *
#from routing import router
#import m3.components as m3
import anvil.server
import anvil.users
#import anvil.js
from ... import globals

class home_de(home_deTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def testen_button_click(self, **event_args):
    globals.testen_button()
    pass

  def impressum_link_click(self, **event_args):
    open_form("home.impressum")
    pass

  def pricing_link_click(self, **event_args):
    self.pricing_label.scroll_into_view()
    pass

  def data_protection_link_click(self, **event_args):
    open_form("home.data_protection")
    pass
