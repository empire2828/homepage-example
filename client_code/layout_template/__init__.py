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

  def show_multiframe(self, iframe_index):
    """Zeigt multiframe an und lädt den gewünschten IFrame"""
    print(f"[LAYOUT] show_multiframe({iframe_index}) aufgerufen")
  
    # Erstelle multiframe nur einmal
    if not hasattr(globals, 'current_multiframe_instance') or globals.current_multiframe_instance is None:
      print("[LAYOUT] Erstelle multiframe und füge es zum content_panel hinzu")
      globals.current_multiframe_instance = multiframe()
      # Füge als Komponente hinzu
      self.content_panel.clear()
      self.content_panel.add_component(globals.current_multiframe_instance,full_width_row=True)
    else:
      print(f"[LAYOUT] Multiframe existiert bereits, verwende es")
  
      # Zeige den gewünschten IFrame
    print(f"[LAYOUT] Rufe lade_und_zeige_iframe({iframe_index}) auf")
    globals.current_multiframe_instance.lade_und_zeige_iframe(iframe_index)
    print(f"[LAYOUT] show_multiframe({iframe_index}) FERTIG")

  def hide_multiframe(self):
    """Versteckt alle IFrames (z.B. wenn andere Seite angezeigt wird)"""
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.verstecke_alle_iframes()

  def show_other_content(self, form_name):
    """Zeigt andere Inhalte im content_panel"""
    print(f"[LAYOUT] show_other_content({form_name}) aufgerufen")
  
    # Verstecke alle IFrames in multiframe (aber behalte multiframe im Panel!)
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      print(f"[LAYOUT] Verstecke alle IFrames")
      globals.current_multiframe_instance.visible = False  # NEU: nur unsichtbar machen
      globals.current_multiframe_instance.verstecke_alle_iframes()
  
      # NICHT clear() aufrufen! Das löscht die multiframe Komponente!
      # Stattdessen: Leere nur den sichtbaren Bereich
  
      # Füge neue Komponente hinzu (neben der unsichtbaren multiframe)
    print(f"[LAYOUT] Füge neue Komponente hinzu: {form_name}")
  
    if form_name == 'channel_manager_connect':
      from ..channel_manager_connect import channel_manager_connect
      self.content_panel.add_component(channel_manager_connect(),full_width_row=True)
    elif form_name == 'my_account':
      from ..my_account import my_account
      self.content_panel.add_component(my_account(),full_width_row=True)
    elif form_name == 'knowledge_hub':
      from ..knowledge_hub import knowledge_hub
      self.content_panel.add_component(knowledge_hub(),full_width_row=True)
    elif form_name == 'upgrade':
      from ..upgrade import upgrade
      self.content_panel.add_component(upgrade(),full_width_row=True)
  
    print(f"[LAYOUT] show_other_content({form_name}) FERTIG")


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

  def _show_dashboard_iframe(self, index, link_to_select):
    """Generische Methode um einen IFrame anzuzeigen"""
    print(f"[DEBUG] _show_dashboard_iframe({index}) aufgerufen")
  
    # Mache multiframe wieder sichtbar
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      print(f"[DEBUG] Mache multiframe sichtbar")
      globals.current_multiframe_instance.visible = True
    else:
      print("[DEBUG] FEHLER: current_multiframe_instance ist None!")
      return
  
      # IFrame laden
    try:
      print(f"[DEBUG] Rufe show_multiframe({index}) auf")
      self.show_multiframe(index)
      print(f"[DEBUG] show_multiframe({index}) erfolgreich")
    except Exception as e:
      print(f"[DEBUG] FEHLER in show_multiframe: {e}")
      import traceback
      traceback.print_exc()
      return
  
    try:
      print(f"[DEBUG] Rufe reset_links() auf")
      self.reset_links()
      print(f"[DEBUG] reset_links() erfolgreich")
    except Exception as e:
      print(f"[DEBUG] FEHLER in reset_links: {e}")
      return
  
    try:
      print(f"[DEBUG] Setze Link selected = True")
      link_to_select.selected = True
      print(f"[DEBUG] Link selektiert")
    except Exception as e:
      print(f"[DEBUG] FEHLER beim Setzen des Links: {e}")
      return
  
    try:
      print(f"[DEBUG] Rufe check_if_upgrade_needed() auf")
      self.check_if_upgrade_needed()
      print(f"[DEBUG] check_if_upgrade_needed() erfolgreich")
    except Exception as e:
      print(f"[DEBUG] FEHLER in check_if_upgrade_needed: {e}")
      return
  
    print(f"[DEBUG] _show_dashboard_iframe({index}) KOMPLETT FERTIG")


  def dashboard_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True 
    self._show_dashboard_iframe(0, self.dashboard_navigation_link)

  def monthly_outlook_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(1, self.monthly_outlook_navigation_link)


  def profitability_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(2, self.profitability_navigation_link)

  def bookings_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(3, self.bookings_navigation_link)

  def cancellations_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(4, self.cancellations_navigation_link)

  def occupancy_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(5, self.occupancy_navigation_link)

  def lead_time_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(6, self.lead_time_navigation_link)

  def guest_insights_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(7, self.guest_insights_navigation_link)

  def long_trends_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(8, self.long_trends_navigation_link)

  def detailed_bookings_navigation_link_click(self, **event_args):
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = True  
    self._show_dashboard_iframe(9, self.detailed_bookings_navigation_link)

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    self.show_other_content('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    print(f"[CLICK HANDLER] my_account_navigation_link_click aufgerufen")
  
    # Verstecke multiframe
    if hasattr(globals, 'current_multiframe_instance') and globals.current_multiframe_instance:
      globals.current_multiframe_instance.visible = False
      print('verstecke current multiframe instance')
  
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
