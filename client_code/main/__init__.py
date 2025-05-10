from ._anvil_designer import mainTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#C6ZZPAPN4YYF5NVJ for anvil_extras

class main(mainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
