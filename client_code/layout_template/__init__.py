from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
from ..LookerStudio.multiframe import multiframe
from .. import globals
import anvil.js

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def is_mobile(self):
    """Prüft ob Mobile View"""
    return anvil.js.window.innerWidth < 768

  def get_or_create_multiframe(self):
    """Erstelle multiframe nur einmal und füge EINMALIG hinzu"""
    if not hasattr(globals, 'current_multiframe_instance') or globals.current_multiframe_instance is None:
      print("[layout template] get_or_create multiframe: Erstelle NEUES multiframe")
      globals.current_multiframe_instance = multiframe()
      # 🔥 Nicht mehr in content_panel_iframe, sondern in content Slot!
      self.content.add_component(globals.current_multiframe_instance, full_width_row=True)
      globals.multiframe_open = True
    return globals.current_multiframe_instance

  def show_dashboard(self, iframe_index, link):
    """Zeige einen Dashboard-IFrame"""
    print(f"[layout template] show_dashboard({iframe_index}) START")

    # Multiframe holen und sichtbar machen
    multiframe_obj = self.get_or_create_multiframe()
    multiframe_obj.visible = True

    # 🔥 Laden direkt in den Slot statt in content_panel_iframe
    self.content.clear()  # Slot leeren
    self.content.add_component(multiframe_obj, full_width_row=True)

    if self.is_mobile():
      multiframe_obj.lade_iframe_mobile(iframe_index)
    else:
      multiframe_obj.lade_und_zeige_iframe(iframe_index)

    self.reset_links()
    link.selected = True
    #self.current_user = globals.current_user
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
    self.help_link.selected = False
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

  def help_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('help')
    self.reset_links()
    self.help_link.selected = True

  def upgrade_navigation_link_click(self, **event_args):
    globals.current_multiframe_instance = None
    globals.multiframe_open = False
    open_form('upgrade')
    self.reset_links()
    self.upgrade_navigation_link.selected = True

  def check_if_upgrade_needed(self):
    if globals.user_has_subscription is None:
      return False    #server function not yet ready
    if globals.user_has_subscription is False:
      globals.request_count = anvil.server.call_s('add_request_count', globals.current_user) 
      self.upgrade_navigation_link.badge = True
      self.upgrade_navigation_link.badge_count = int(getattr(globals, "request_count", 0)) 
      print("[layout_emplate] check_if_upgrade_needed:",globals.user_has_subscription)

      if globals.request_count> 20:
        open_form('upgrade_needed')


   


