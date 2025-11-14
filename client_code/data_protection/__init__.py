from ._anvil_designer import data_protectionTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.server
import anvil.google.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil_extras import routing

@routing.route('data_protection')
class data_protection(data_protectionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def back_link_click(self, **event_args):
    open_form('home.home_start')
    pass
