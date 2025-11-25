from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
from ..LookerStudio.multiframe import multiframe
from .. import globals

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_multiframe = None  # Eingebettetes multiframe

    if getattr(globals, "user_has_subscription", None) is False:
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0))

  def show_multiframe(self, iframe_index):
    """Zeigt multiframe an und lädt den gewünschten IFrame"""
    # Erstelle multiframe nur einmal und füge es zum content_panel hinzu
    if self.current_multiframe is None:
      print("[LAYOUT] Erstelle multiframe und füge es zum content_panel hinzu")
      self.current_multiframe = multiframe()
      # WICHTIG: Füge als Komponente hinzu, NICHT open_form!
      self.content.clear()
      self.content.add_component(self.current_multiframe)

    # Zeige den gewünschten IFrame
    self.current_multiframe.lade_und_zeige_iframe(iframe_index)

  def hide_multiframe(self):
    """Versteckt alle IFrames (z.B. wenn andere Seite angezeigt wird)"""
    if self.current_multiframe:
      self.current_multiframe.verstecke_alle_iframes()

  def show_other_content(self, form_name):
    """Zeigt andere Inhalte im content_panel"""
    # Verstecke multiframe IFrames aber behalte es im DOM
    if self.current_multiframe:
      self.current_multiframe.visible = False

    # Lade andere Form als Komponente
    self.content.clear()
    # Füge multiframe wieder hinzu (unsichtbar) damit es im DOM bleibt
    if self.current_multiframe:
      self.content.add_component(self.current_multiframe)
      self.current_multiframe.visible = False

    # Füge neue Komponente hinzu
    if form_name == 'channel_manager_connect':
      from ..channel_manager_connect import channel_manager_connect
      self.content.add_component(channel_manager_connect())
    elif form_name == 'my_account':
      from ..my_account import my_account
      self.content.add_component(my_account())
    elif form_name == 'knowledge_hub':
      from ..knowledge_hub import knowledge_hub
      self.content.add_component(knowledge_hub())
    elif form_name == 'upgrade':
      from ..upgrade import upgrade
      self.content.add_component(upgrade())

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
    self.upgrade_navigation_link.selected = False

  def dashboard_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(0)
    self.reset_links()
    self.dashboard_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def monthly_outlook_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(1)
    self.reset_links()
    self.monthly_outlook_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def profitability_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(2)
    self.reset_links()
    self.profitability_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def bookings_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(3)
    self.reset_links()
    self.bookings_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def cancellations_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(4)
    self.reset_links()
    self.cancellations_navigation_link.selected = True
    self.check_if_upgrade_needed()

  def occupancy_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(5)
    self.reset_links()
    self.occupancy_navigation_link.selected = True
    self.check_if_upgrade_needed()

  def lead_time_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(6)
    self.reset_links()
    self.lead_time_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def guest_insights_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(7)
    self.reset_links()
    self.guest_insights_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def long_trends_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(8)
    self.reset_links()
    self.long_trends_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def detailed_bookings_navigation_link_click(self, **event_args):
    if self.current_multiframe:
      self.current_multiframe.visible = True
    self.show_multiframe(9)
    self.reset_links()
    self.detailed_bookings_navigation_link.selected = True
    self.check_if_upgrade_needed() 

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    self.show_other_content('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    self.show_other_content('my_account')

  def knowledge_hub_link_click(self, **event_args):
    self.reset_links()
    self.knowledge_hub_link.selected = True
    self.show_other_content('knowledge_hub')

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    self.upgrade_navigation_link.selected = True
    self.show_other_content('upgrade')

  def check_if_upgrade_needed(self, **event_args):
    result = anvil.server.call_s('add_request_count', globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count
