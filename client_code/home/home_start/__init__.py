from ._anvil_designer import home_startTemplate
from anvil import *
import anvil.server
import anvil.users
from anvil.tables import app_tables

class home_start(home_startTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    user_locale = anvil.js.window.navigator.language
    if user_locale.lower().startswith("de"):
      open_form('home.home_de')
    else:
      open_form('home.home_en')