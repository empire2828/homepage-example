from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..LookerStudio.multiframe import multiframe
from ..LookerStudio.bookings import bookings

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)    
    #self.multiframe_form = multiframe()
    self.bookings_form= bookings()

    # Füge die multiframe Form zu einem ContentPanel hinzu (z.B. main_content_panel)
    # Annahme: Du hast ein ContentPanel namens "content_panel" oder ähnlich
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
    pass

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    if get_open_form().LookerStudio.bookings.visible:
      get_open_form().LookerStudio.bookings.visible = False
    else:
      get_open_form().LookerStudio.bookings.visible = True
    pass

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    self.multiframe_form.setze_sichtbares_iframe(3)  # Index 1 für Profitability
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

  

  

  
 
