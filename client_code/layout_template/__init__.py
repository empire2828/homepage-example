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
      print("[DEBUG] Erstelle NEUES multiframe")
      globals.current_multiframe_instance = multiframe()
      self.content_panel_iframe.add_component(globals.current_multiframe_instance, full_width_row=True)
      print(f"[DEBUG] multiframe zu content_panel hinzugefügt")
      globals.multiframe_open = True
    return globals.current_multiframe_instance

  def show_dashboard(self, iframe_index, link):
    """Zeige einen Dashboard-IFrame"""
    print(f"[LAYOUT] show_dashboard({iframe_index}) START")

    # Multiframe holen und sichtbar machen
    multiframe_obj = self.get_or_create_multiframe()
    multiframe_obj.visible = True

    # IFrame laden/anzeigen
    multiframe_obj.lade_und_zeige_iframe(iframe_index)

    self.reset_links()
    link.selected = True
    self.check_if_upgrade_needed()
    print(f"[LAYOUT] show_dashboard({iframe_index}) FERTIG")

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
    if globals.multiframe_open:
      self.show_dashboard(0, self.dashboard_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(0, layout_form.dashboard_navigation_link)

  def monthly_outlook_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(1, self.monthly_outlook_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(1, layout_form.monthly_outlook_navigation_link)

  def profitability_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(2, self.profitability_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(2, layout_form.profitability_navigation_link)

  def bookings_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(3, self.bookings_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(3, layout_form.bookings_navigation_link)

  def cancellations_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(4, self.cancellations_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(4, layout_form.cancellations_navigation_link)

  def occupancy_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(5, self.occupancy_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(5, layout_form.occupancy_navigation_link)

  def lead_time_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(6, self.lead_time_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(6, layout_form.lead_time_navigation_link)

  def guest_insights_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(7, self.guest_insights_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(7, layout_form.guest_insights_navigation_link)

  def long_trends_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(8, self.long_trends_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(8, layout_form.long_trends_navigation_link)

  def detailed_bookings_navigation_link_click(self, **event_args):
    if globals.multiframe_open:
      self.show_dashboard(9, self.detailed_bookings_navigation_link)
    else:
      layout_form = open_form('layout_template')
      layout_form.show_dashboard(9, layout_form.detailed_bookings_navigation_link)

  def connect_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('channel_manager_connect')
    self.reset_links()
    self.connect_navigation_link.selected = True

  def my_account_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('my_account')
    self.reset_links()
    self.my_account_navigation_link.selected = True

  def knowledge_hub_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('knowledge_hub')
    self.reset_links()
    self.knowledge_hub_link.selected = True


  def upgrade_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('upgrade')
    self.reset_links()
    self.upgrade_navigation_link.selected = True

  def check_if_upgrade_needed(self):
    result = anvil.server.call_s('add_request_count', globals.current_user)
    try:
      globals.request_count = int(result)
    except (TypeError, ValueError):
      globals.request_count = 0
    self.upgrade_navigation_link.badge_count = globals.request_count

