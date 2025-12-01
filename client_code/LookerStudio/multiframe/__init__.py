from ._anvil_designer import multiframeTemplate
from anvil import *
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json
from ... import globals

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/f501eb07-1cff-4de0-9a92-a929c72f01f6/page/"

  def __init__(self, **properties):
    self.init_components(**properties)
    #self.flow_panel_1.scroll_into_view(smooth=True)
    self.current_user = globals.current_user
    self.supabase_key = ""

    if self.current_user is None:
      print("[multiframe] Warnung: Kein current_user verfügbar")
      return

    if self.current_user.get('smoobu_api_key') is None:
      open_form('channel_manager_connect')
    else:
      self.supabase_key = self.current_user.get('supabase_key', '')

      if self.supabase_key:
        self.content_panel.visible = True
        print(f"[multiframe] init {globals.current_user['email']} supabase key: {self.supabase_key}")
      else:
        print(f"{self.current_user['email']} Warnung: Kein supabase_key verfügbar")  

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
      panel.height = 2000

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if index < 0 or index >= len(self.iframe_urls):        
      print("[multiframe] erstelle_iframe ",self.current_user['email'],f"Ungültiger Index: {index}")
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
      "height": "1950",
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
    #print("erstelle_iframe als geladen markieren self.geladene_iframes:",self.geladene_iframes)

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    #print(f"[MULTIFRAME] lade_und_zeige_iframe({index}) START")
  
    if index < 0 or index >= len(self.iframe_urls):
      print(self.current_user['email']," ",f"Ungültiger Index: {index}")
      return
  
    #print(f"[MULTIFRAME] Index {index} ist gültig")
  
    # OPTIMIERUNG: Wenn bereits angezeigt, nichts tun
    if self.aktueller_index == index:
      #print(f"[MULTIFRAME] IFrame {index} ist bereits sichtbar, überspringe")
      return
  
    #print(f"[MULTIFRAME] aktueller_index ({self.aktueller_index}) != index ({index})")
  
    # OPTIMIERUNG: Nur vorheriges Panel verstecken statt alle
    if self.aktueller_index is not None:
        #print(f"[MULTIFRAME] Verstecke vorheriges Panel {self.aktueller_index}")
        self.panels[self.aktueller_index].visible = False
  
    # IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      #print(f"[MULTIFRAME] IFrame {index} wird erstmalig geladen...")
      self.erstelle_iframe(index)
    #else:
      #print(f"[MULTIFRAME] IFrame {index} bereits geladen")

    # Gewünschtes Panel anzeigen
    #print(f"[MULTIFRAME] Zeige Panel {index}")
    self.panels[index].visible = True
    self.aktueller_index = index
    #print(f"[MULTIFRAME] lade_und_zeige_iframe({index}) FERTIG, aktueller_index: {self.aktueller_index}")

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
      #print("ist_geladen ","False Index:",index," len(self.geladene_iframes:",len(self.geladene_iframes))
      return False
    return self.geladene_iframes[index]

  def lade_alle_iframes(self):
    """Lädt alle IFrames im Voraus (falls gewünscht für bessere Performance)"""
    for i in range(len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
    print("Alle IFrames geladen")

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
    pass

  def lade_restliche_iframes(self):
    """Lädt IFrames 1-10 im Hintergrund"""
    for i in range(1, len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
        print("[multiframe] lade_restliche_iframses erstelle iframe",i)

  def lade_iframe_mobile(self, index):
    """Einfaches IFrame laden für Mobile - OHNE Caching/Status - nutzt nur erstes Panel"""
    if index < 0 or index >= len(self.iframe_urls):
      print(f"[multiframe mobile] Ungültiger Index: {index}")
      return

    url = self.iframe_urls[index]

    # Parameter für Supabase Key hinzufügen
    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
    else:
      iframe_url = url

    # Nur das ERSTE Panel nutzen für Mobile
    panel = self.panels[0]

    # 1. Zuerst: Alle iframes explizit entfernen (wichtig für Memory!)
    jQuery(get_dom_node(panel)).find('iframe').remove()

    # 2. Dann: Panel komplett leeren (falls noch was übrig ist)
    jQuery(get_dom_node(panel)).empty()

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1000",
      "frameborder": "0",
      "scrolling": "no",
      #"style": "border:0; position: relative; z-index: 1; overflow: visible;",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox": "allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    })

    iframe.appendTo(get_dom_node(panel))
    panel.visible = True

    print(f"[multiframe mobile] IFrame {index} einfach in Panel 0 geladen (kein Cache)")


