from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)    
    self.form_show()
    # Any code you write here will run before the form opens.

  def reset_links(self, **event_args):
    self.dashboard_navigation_link.selected= False
    self.channel_manager_connect_navigation_link.selected = False
    self.upgrade_navigation_link.selected = False
    self.my_account_navigation_link.selected = False

  def dashboard_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def channel_manager_connect_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def help_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def form_show(self, **event_args):
    pass
 
