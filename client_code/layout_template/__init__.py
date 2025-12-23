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

  def show_dashboard(self, iframe_index, link):
    #für initialen Aufruf nach Login
    print(f"[layout template] ({iframe_index}) START")

    if self.is_mobile():
      # MOBILE: Öffne multiframe mit dem Dashboard-Index
      open_form('LookerStudio.multiframe', dashboard_index=iframe_index)
    else:
      # DESKTOP: Nutze das bestehende Multiframe mit allen Panels
      multiframe_obj = self.get_or_create_multiframe()
      multiframe_obj.visible = True
      multiframe_obj.lade_und_zeige_iframe(iframe_index)

    self.reset_links()
    link.selected = True
    self.check_if_upgrade_needed()
  
  def get_or_create_multiframe(self):
    # für initialen Aufruf druch Show Dashboard nach Login
    if not hasattr(globals, 'current_multiframe_instance') or globals.current_multiframe_instance is None:
      print("[layout template] Multiframe wird über open_form geladen")
      open_form('LookerStudio.multiframe')
      globals.multiframe_open = True
    return globals.current_multiframe_instance

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

  def _handle_menu_click(self, index, link):
    """Universal handler - erstellt multiframe neu falls nötig"""
  
    # Falls multiframe gelöscht wurde, neu erstellen
    if not globals.current_multiframe_instance:
      print("[layout template] Multiframe wird neu initialisiert")
      open_form('LookerStudio.multiframe', dashboard_index=index)
      # WICHTIG: return hier, warte bis Form geladen ist
      return
  
      # Nur wenn bereits vorhanden:
    if self.is_mobile():
      globals.current_multiframe_instance.lade_iframe_mobile(index)
    else:
      globals.current_multiframe_instance.lade_und_zeige_iframe(index)
  
    self.reset_links()
    link.selected = True

  def dashboard_navigation_link_click(self, **event_args):
    # Multiframe ist bereits da, zeige einfach den Dashboard an
    self._handle_menu_click(0,self.dashboard_navigation_link)

  def monthly_outlook_navigation_link_click(self, **event_args):
    self._handle_menu_click(1,self.monthly_outlook_navigation_link)

  def profitability_navigation_link_click(self, **event_args):
    self._handle_menu_click(2,self.profitability_navigation_link)

  def bookings_navigation_link_click(self, **event_args):
    self._handle_menu_click(3,self.bookings_navigation_link)

  def cancellations_navigation_link_click(self, **event_args):
     self._handle_menu_click(4,self.cancellations_navigation_link)

  def occupancy_navigation_link_click(self, **event_args):
    self._handle_menu_click(5,self.occupancy_navigation_link)

  def lead_time_navigation_link_click(self, **event_args):
    self._handle_menu_click(6,self.lead_time_navigation_link)

  def guest_insights_navigation_link_click(self, **event_args):
    self._handle_menu_click(7,self.guest_insights_navigation_link)

  def long_trends_navigation_link_click(self, **event_args):
    self._handle_menu_click(8,self.long_trends_navigation_link)

  def detailed_bookings_navigation_link_click(self, **event_args):
    self._handle_menu_click(9,self.detailed_bookings_navigation_link)

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


   


