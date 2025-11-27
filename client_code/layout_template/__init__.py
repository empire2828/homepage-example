from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
from ..LookerStudio.multiframe import multiframe
from .. import globals

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if getattr(globals, "user_has_subscription", None) is False:
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0))

  def get_or_create_multiframe(self):
    """Erstelle multiframe nur einmal und füge EINMALIG hinzu"""
    if not hasattr(globals, 'current_multiframe_instance') or globals.current_multiframe_instance is None:
      globals.current_multiframe_instance = multiframe()
      self.content_panel_iframe.add_component(globals.current_multiframe_instance, full_width_row=True)
    return globals.current_multiframe_instance

  def show_dashboard(self, iframe_index, link):
    """Zeige einen Dashboard-IFrame"""
    multiframe_obj = self.get_or_create_multiframe()
    multiframe_obj.visible = True
    multiframe_obj.lade_und_zeige_iframe(iframe_index)

    self.reset_links()
    link.selected = True
    self.check_if_upgrade_needed()

  def reset_links(self):
    """Deselektiere alle Navigation Links"""
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
    self.upgrade_navigation_link.selected = False

  def dashboard_navigation_link_click(self, **event_args):
    self.show_dashboard(0, self.dashboard_navigation_link)

  def monthly_outlook_navigation_link_click(self, **event_args):
    self.show_dashboard(1, self.monthly_outlook_navigation_link)

  def profitability_navigation_link_click(self, **event_args):
    self.show_dashboard(2, self.profitability_navigation_link)

  def bookings_navigation_link_click(self, **event_args):
    self.show_dashboard(3, self.bookings_navigation_link)

  def cancellations_navigation_link_click(self, **event_args):
    self.show_dashboard(4, self.cancellations_navigation_link)

  def occupancy_navigation_link_click(self, **event_args):
    self.show_dashboard(5, self.occupancy_navigation_link)

  def lead_time_navigation_link_click(self, **event_args):
    self.show_dashboard(6, self.lead_time_navigation_link)

  def guest_insights_navigation_link_click(self, **event_args):
    self.show_dashboard(7, self.guest_insights_navigation_link)

  def long_trends_navigation_link_click(self, **event_args):
    self.show_dashboard(8, self.long_trends_navigation_link)

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.show_dashboard(9, self.detailed_bookings_navigation_link)

  def connect_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    open_form('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    open_form('my_account')

  def knowledge_hub_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    open_form('knowledge_hub')

  def upgrade_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    open_form('upgrade')

  def check_if_upgrade_needed(self):
    result = anvil.server.call_s('add_request_count', globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count
