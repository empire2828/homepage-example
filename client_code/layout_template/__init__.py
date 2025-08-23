from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
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
    self.profitability_navigation_link.selected= False
    self.bookings_navigation_link.selected= False
    self.cancellations_navigation_link.selected= False
    self.occupancy_navigation_link.selected= False
    self.lead_time_navigation_link.selected= False
    self.guest_insights_navigation_link.selected= False
    self.detailed_bookings_navigation_link.selected= False
    self.long_trends_navigation_link.selected= False
    self.connect_navigation_link.selected = False
    self.my_account_navigation_link.selected = False

  def dashboard_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def form_show(self, **event_args):
    pass

  def profitability_navigation_link_click(self, **event_args):
    self.reset_links()
    multiframe.looker_flow_panel_copy.visible
    pass

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def occupancy_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def lead_time_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def guest_insights_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def long_trends_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  

  

  
 
