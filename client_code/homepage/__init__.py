from ._anvil_designer import homepageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class homepage(homepageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def login_button_click(self, **event_args):
   user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True, allow_remembered=True)
   if user:
    open_form('dashboard')
    pass

  def outlined_button_1_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
     open_form('dashboard')
     pass
