from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
from ..LookerStudio.multiframe import multiframe
from .. import globals

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)    
    self.current_multiframe = None

    # Cache navigation links
    self._nav_links = [
      self.dashboard_navigation_link,
      self.monthly_outlook_navigation_link,
      self.profitability_navigation_link,
      self.bookings_navigation_link,
      self.cancellations_navigation_link,
      self.occupancy_navigation_link,
      self.lead_time_navigation_link,
      self.guest_insights_navigation_link,
      self.detailed_bookings_navigation_link,
      self.long_trends_navigation_link,
      self.connect_navigation_link,
      self.knowledge_hub_link,
      self.my_account_navigation_link,
      self.upgrade_navigation_link
    ]

    if getattr(globals, "user_has_subscription", None) is False:
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0))

  def ensure_multiframe(self):
    """Erstellt multiframe nur einmal und fügt es in content_panel ein"""
    if not self.current_multiframe:
      self.current_multiframe = multiframe()
      # Annahme: Sie haben ein content_panel im layout_template Designer
      # Falls nicht, nutzen Sie self.content_panel oder einen anderen Container
      self.content_panel.clear()
      self.content_panel.add_component(self.current_multiframe)
    return self.current_multiframe

  def reset_links(self):
    self.layout.hide_nav_drawer()
    for link in self._nav_links:
      link.selected = False

  def _navigate_to_iframe(self, link, iframe_index):
    """Optimierte Navigation - KEIN open_form mehr!"""
    self.reset_links()
    link.selected = True
    self.check_if_upgrade_needed() 

    # Multiframe wird nur einmal erstellt, dann nur IFrame gewechselt
    multiframe_form = self.ensure_multiframe()
    multiframe_form.lade_und_zeige_iframe(iframe_index)

  def dashboard_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.dashboard_navigation_link, 0)

  def monthly_outlook_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.monthly_outlook_navigation_link, 1)

  def profitability_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.profitability_navigation_link, 2)

  def bookings_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.bookings_navigation_link, 3)

  def cancellations_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.cancellations_navigation_link, 4)

  def occupancy_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.occupancy_navigation_link, 5)

  def lead_time_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.lead_time_navigation_link, 6)

  def guest_insights_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.guest_insights_navigation_link, 7)

  def long_trends_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.long_trends_navigation_link, 8)

  def detailed_bookings_navigation_link_click(self, **event_args):
    self._navigate_to_iframe(self.detailed_bookings_navigation_link, 9)

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    open_form('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    open_form('my_account')

  def knowledge_hub_link_click(self, **event_args):
    self.reset_links()
    self.knowledge_hub_link.selected = True
    open_form('knowledge_hub')

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    self.upgrade_navigation_link.selected = True
    open_form('upgrade')

  def check_if_upgrade_needed(self, **event_args):
    result = anvil.server.call_s('add_request_count', globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count
