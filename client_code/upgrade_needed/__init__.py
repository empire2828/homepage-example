from ._anvil_designer import upgrade_neededTemplate
from anvil import *
import anvil.server
from routing import router
import m3.components as m3
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class upgrade_needed(upgrade_neededTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
    pass
