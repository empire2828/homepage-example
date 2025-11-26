from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
from ..LookerStudio.multiframe import multiframe
from .. import globals

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_other_component = None  # Speichert aktuelle Nicht-Dashboard-Komponente

    if getattr(globals, "user_has_subscription", None) is False:
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0))

  def get_or_create_multiframe(self):
    """Erstelle multiframe nur einmal und füge EINMALIG hinzu"""
    if not hasattr(globals, 'current_multiframe_instance') or globals.current_multiframe_instance is None:
      print("[DEBUG] Erstelle NEUES multiframe")
      globals.current_multiframe_instance = multiframe()
      self.content_panel.add_component(globals.current_multiframe_instance, full_width_row=True)
      print(f"[DEBUG] multiframe zu content_panel hinzugefügt, Panel hat jetzt {len(self.content_panel.get_components())} Komponenten")
    return globals.current_multiframe_instance

  def show_dashboard(self, iframe_index, link):
    """Zeige einen Dashboard-IFrame"""
    # Entferne alte Komponente falls vorhanden
    if self.current_other_component is not None:
      self.current_other_component.remove_from_parent()
      self.current_other_component = None

    self.content_panel.visible = True
    self.content_panel.clear()

    multiframe_obj = self.get_or_create_multiframe()
    multiframe_obj.visible = True
    multiframe_obj.lade_und_zeige_iframe(iframe_index)

    self.reset_links()
    link.selected = True
    self.check_if_upgrade_needed()

  def show_other_page(self, form_name, link):
    """Zeige eine andere Seite (My Account, etc.)"""

    # Entferne alte Komponente falls vorhanden
    if self.current_other_component is not None:
      self.current_other_component.remove_from_parent()
      self.current_other_component = None

    self.init_components()

    # Erstelle und speichere neue Komponente
    if form_name == 'channel_manager_connect':
      from ..channel_manager_connect import channel_manager_connect
      self.current_other_component = channel_manager_connect()
      self.content_panel.add_component(self.current_other_component, full_width_row=True)  
    elif form_name == 'test':
      from ..test import test
      self.current_other_component = test()
      self.content_panel.add_component(self.current_other_component, full_width_row=True) 
    elif form_name == 'my_account':
      open_form('my_account')
    elif form_name == 'knowledge_hub':
      from ..knowledge_hub import knowledge_hub
      self.current_other_component = knowledge_hub()
      self.content_panel.add_component(self.current_other_component, full_width_row=True)
    elif form_name == 'upgrade':
      from ..upgrade import upgrade
      self.current_other_component = upgrade()
      self.content_panel.add_component(self.current_other_component, full_width_row=True)

    self.reset_links()
    link.selected = True

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
    self.show_other_page('channel_manager_connect', self.connect_navigation_link)

  def my_account_navigation_link_click(self, **event_args):
    self.show_other_page('my_account', self.my_account_navigation_link)

  def knowledge_hub_link_click(self, **event_args):
    self.show_other_page('knowledge_hub', self.knowledge_hub_link)

  def upgrade_navigation_link_click(self, **event_args):
    self.show_other_page('upgrade', self.upgrade_navigation_link)

  def check_if_upgrade_needed(self):
    result = anvil.server.call_s('add_request_count', globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count

  def navigation_link_1_click(self, **event_args):
        self.show_other_page('test', self.navigation_link_1)
