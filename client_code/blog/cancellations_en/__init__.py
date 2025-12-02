from ._anvil_designer import cancellations_enTemplate
from anvil import *
from routing import router
#import m3.components as m3
import anvil.server
#import anvil.google.auth, anvil.google.drive
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
#from ... import globals

class cancellations_en(cancellations_enTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def learn_more_button_click(self, **event_args):
    open_form('home.home_en')
    pass
