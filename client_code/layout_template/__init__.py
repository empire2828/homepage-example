from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
#import anvil.users
from ..LookerStudio.multiframe import multiframe
from .. import globals

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)    
    self.current_multiframe = None

    if getattr(globals, "user_has_subscription", None) is False:
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0))

  def open_multiframe_form(self):
    if not self.current_multiframe:
      self.current_multiframe = multiframe()
      open_form(self.current_multiframe)
    else:
      # Multiframe ist bereits geöffnet, nur sicherstellen dass es die aktive Form ist
      if get_open_form() != self.current_multiframe:
        open_form(self.current_multiframe)
    return self.current_multiframe

  def reset_links(self, **event_args):
    self.layout.hide_nav_drawer()
    self.dashboard_navigation_link.selected = False
    self.monthly_outlook_navigation_link.selected = False
    self.profitability_navigation_link.selected = False
    self.bookings_navigation_link.selected = False
    self.cancellations_navigation_link.selected = False
    self.occupancy_navigation_link.selected = False
    self.lead_time_navigation_link.selected = False
    self.guest_insights_navigation_link.selected = False
    self.detailed_bookings_navigation_link.selected = False
    self.long_trends_navigation_link.selected = False
    self.connect_navigation_link.selected = False
    self.knowledge_hub_link.selected = False
    self.my_account_navigation_link.selected = False
    self.upgrade_navigation_link.selected= False

  def dashboard_navigation_link_click(self, **event_args):
    self.reset_links()
    self.dashboard_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(0)  # Dashboard

  def monthly_outlook_navigation_link_click(self, **event_args):
    self.reset_links()
    self.monthly_outlook_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(1)  # Dashboard

  def profitability_navigation_link_click(self, **event_args):
    self.reset_links()
    self.profitability_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(2)  # Profitability

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.bookings_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(3)  # Long Trends

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    self.cancellations_navigation_link.selected = True
    self.check_if_upgrade_needed()
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(4)  # Cancellations

  def occupancy_navigation_link_click(self, **event_args):
    self.reset_links()
    self.occupancy_navigation_link.selected = True
    self.check_if_upgrade_needed()
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(5)  # Occupancy

  def lead_time_navigation_link_click(self, **event_args):
    self.reset_links()
    self.lead_time_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(6)  # Lead Time

  def guest_insights_navigation_link_click(self, **event_args):
    self.reset_links()
    self.guest_insights_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(7)  # Guest Insights

  def long_trends_navigation_link_click(self, **event_args):
    self.reset_links()
    self.long_trends_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(8)  # Long Trends

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.detailed_bookings_navigation_link.selected = True
    self.check_if_upgrade_needed() 
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(9)  # Detailed Bookings

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    open_form('channel_manager_connect')
    pass

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    open_form('my_account')
    pass

  def knowledge_hub_link_click(self, **event_args):
    self.reset_links()
    self.knowledge_hub_link.selected = True
    open_form('knowledge_hub')
    pass

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    self.upgrade_navigation_link.selected = True
    open_form('upgrade')
    pass

  def check_if_upgrade_needed(self, **event_args):
    result = anvil.server.call_s('add_request_count',globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count
    return

