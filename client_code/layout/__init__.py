from ._anvil_designer import layoutTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class layout(layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def home_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('home')

  def guestscreen_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('guestscreen')

  def reset_links(self, **event_args):
    self.home_link.role = ''
    self.guestscreen_link.role = ''
