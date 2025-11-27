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
    from ._anvil_designer import multiframeTemplate
from anvil import *
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json
from ... import globals

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/1eaf8e1d-9780-4e7c-9d4f-f0f392694afc/page/"

  def __init__(self, **properties):
    self.init_components(**properties)
    #self.flow_panel_1.scroll_into_view(smooth=True)
    self.supabase_key= ""  
    self.current_user = globals.current_user
    request_count= int(globals.request_count)

    if request_count > 20:
      is_user_below_request_count = False
    else:
      is_user_below_request_count = True

    if self.current_user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.channel_manager_connect_button.visible = True
    else:
      if globals.user_has_subscription is False and is_user_below_request_count is False:
        self.dashboard_upgrade_needed_text_1.visible = True
        self.dashboard_upgrade_needed_text_2.visible = True
        self.dashboard_upgrade_button.visible = True
    if (is_user_below_request_count or globals.user_has_subscription) and self.current_user['smoobu_api_key'] is not None:      
      if self.current_user and 'supabase_key' in self.current_user:
        self.supabase_key = self.current_user['supabase_key']
        self.content_panel.visible = True
      else:
        self.supabase_key = ""
        print(self.current_user['email']," Warnung: Kein supabase_key verfügbar")      
    else: 
      pass      

    self.iframe_urls = [
      f"{self.Locker_Version}qmCOF",            # Dashboard
      f"{self.Locker_Version}p_frni7wm2vd",     # Outlook
      f"{self.Locker_Version}p_8l5lnc13td",     # Profitability
      f"{self.Locker_Version}p_9euf3853td",     # Bookings
      f"{self.Locker_Version}p_knw9h153td",     # Cancellations
      f"{self.Locker_Version}p_1idplf63td",     # Occupancy
      f"{self.Locker_Version}p_8hyzd253td",     # Lead Time
      f"{self.Locker_Version}p_tilmy6zhtd",     # Guest Insights
      f"{self.Locker_Version}p_4dt5tycuud",     # Long Trends     
      f"{self.Locker_Version}p_cc0slxgtud",     # Detailed Bookings
      f"{self.Locker_Version}p_396qlut0wd",     # Knowledge hub
    ]

    self.panels = [
      self.looker_flow_panel_1,
      self.looker_flow_panel_2,
      self.looker_flow_panel_3,
      self.looker_flow_panel_4,
      self.looker_flow_panel_5,
      self.looker_flow_panel_6,
      self.looker_flow_panel_7,
      self.looker_flow_panel_8,
      self.looker_flow_panel_9,
      self.looker_flow_panel_10,
      self.looker_flow_panel_11,
    ]

    # Status-Tracking welche IFrames bereits geladen wurden
    self.geladene_iframes = [False] * len(self.iframe_urls)

    # Aktuell sichtbarer Index
    self.aktueller_index = None

    # Initial: alle Panels unsichtbar
    for i, panel in enumerate(self.panels):
      panel.visible = False
      panel.height = 1000

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if index < 0 or index >= len(self.iframe_urls):        
      print(self.current_user['email'],f"Ungültiger Index: {index}")
      return

    url = self.iframe_urls[index]
    panel = self.panels[index]

    # Parameter für Supabase Key hinzufügen
    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
    else:
      iframe_url = url

    # Vorheriges IFrame entfernen falls vorhanden
    jQuery(get_dom_node(panel)).empty()

    # IFrame erstellen mit expliziten Attributen
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "950",
      "frameborder": "0",
      "scrolling": "no",
      "loading": "lazy",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox":"allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    })

    #"style": "border: none; background: white;",
    #"allow": "fullscreen; storage-access",


    # IFrame zum Panel hinzufügen
    iframe.appendTo(get_dom_node(panel))

    # Als geladen markieren
    self.geladene_iframes[index] = True
    print("erstelle_iframe als geladen markieren self.geladene_iframes:",self.geladene_iframes)

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    print(f"[MULTIFRAME] lade_und_zeige_iframe({index}) START")

    if index < 0 or index >= len(self.iframe_urls):
      print(self.current_user['email']," ",f"Ungültiger Index: {index}")
      return

    print(f"[MULTIFRAME] Index {index} ist gültig")

    # OPTIMIERUNG: Wenn bereits angezeigt, nichts tun
    if self.aktueller_index == index:
      print(f"[MULTIFRAME] IFrame {index} ist bereits sichtbar, überspringe")
      return

    print(f"[MULTIFRAME] aktueller_index ({self.aktueller_index}) != index ({index})")

    # OPTIMIERUNG: Nur vorheriges Panel verstecken statt alle
    if self.aktueller_index is not None:
      print(f"[MULTIFRAME] Verstecke vorheriges Panel {self.aktueller_index}")
      self.panels[self.aktueller_index].visible = False
  
    # IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      print(f"[MULTIFRAME] IFrame {index} wird erstmalig geladen...")
      self.erstelle_iframe(index)
      print("erstelle_iframe als geladen markieren self.geladene_iframes:",self.geladene_iframes)
    else:
      print(f"[MULTIFRAME] IFrame {index} bereits geladen")

    # Gewünschtes Panel anzeigen
    print(f"[MULTIFRAME] Zeige Panel {index}")
    self.panels[index].visible = True
    self.aktueller_index = index
    print(f"[MULTIFRAME] lade_und_zeige_iframe({index}) FERTIG, aktueller_index: {self.aktueller_index}")

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames ohne sie zu entladen"""
    print("Verstecke alle IFrames...")
    for i, panel in enumerate(self.panels):
      panel.visible = False
      print(f"   Panel {i} versteckt")
    self.aktueller_index = None

  def ist_geladen(self, index):
    """Prüft ob IFrame bereits geladen ist"""
    if index < 0 or index >= len(self.geladene_iframes):
      print("ist_geladen ","False Index:",index," len(self.geladene_iframes:",len(self.geladene_iframes))
      return False
    return self.geladene_iframes[index]

  def lade_alle_iframes(self):
    """Lädt alle IFrames im Voraus (falls gewünscht für bessere Performance)"""
    print(f"[MULTIFRAME] Lade alle {len(self.iframe_urls)} IFrames vor...")
    for i in range(len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
    print(f"[MULTIFRAME] Alle IFrames geladen: {self.geladene_iframes}")

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
  

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
