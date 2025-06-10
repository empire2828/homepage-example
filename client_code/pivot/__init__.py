from ._anvil_designer import pivotTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class pivot(pivotTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    pivot_data = anvil.server.call('get_dashboard_data_dict')
    self.pivot_1.items= pivot_data
    # Any code you write here will run before the form opens.
