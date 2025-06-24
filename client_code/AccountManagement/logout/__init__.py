from ._anvil_designer import logoutTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class logout(logoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    result= alert(
      content="Do you want to logout?",
      title="Log off",
      buttons=[
        ("Yes", "YES"),
        ("No", "NO"),
      ])
    if result=="YES":
      anvil.users.logout()
      open_form('homepage')
    pass
