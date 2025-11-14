from ._anvil_designer import impressumTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.google.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class impressum(impressumTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def back_link_click(self, **event_args):
    open_form('home.home_start')
    pass
