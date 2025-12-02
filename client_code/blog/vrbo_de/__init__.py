from ._anvil_designer import vrbo_deTemplate
from anvil import *
import anvil.server
from routing import router
#import m3.components as m3
#import anvil.google.auth, anvil.google.drive
#import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
#from ... import globals

class vrbo_de(vrbo_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def learn_more_button_click(self, **event_args):
    open_form('home.home_de')
    pass