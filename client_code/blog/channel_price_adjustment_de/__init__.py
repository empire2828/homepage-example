from ._anvil_designer import channel_price_adjustment_deTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from routing import router

# import m3.components as m3
import anvil.server

# import anvil.google.auth, anvil.google.drive
import anvil.users
# import anvil.tables as tables
# import anvil.tables.query as q
# from anvil.tables import app_tables
# from ... import globals


class channel_price_adjustment_de(channel_price_adjustment_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def learn_more_button_click(self, **event_args):
    open_form("home.home_de")
    pass
