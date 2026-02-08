from ._anvil_designer import multiframeTemplate
from anvil import *
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json
from ... import globals

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/77533d89-29c4-4a7f-922c-7a6f4a85903f/page/"
  #https://lookerstudio.google.com/embed/reporting/6dc3e355-e5ce-4de8-a09e-c4a785d30b11/page/qmCOF
  #V1.1.10 Freigeben als nicht gelistet und Bericht einbetten aktivieren ohne Berichtsnavi mit URL
  
  def __init__(self, **properties):
    self.init_components(**properties)
    #self.looker_flow_panel_1.scroll_into_view(smooth=False)
    #anvil.js.window.scrollTo(0, 0)
    globals.current_multiframe_instance = self  
    self.current_user = globals.current_user
    self.supabase_key = ""
    self.is_mobile = anvil.js.window.innerWidth < 768

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

    if self.is_mobile:
      self.panels = [self.looker_flow_panel_1]
    else:
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
      if not self.is_mobile:
        panel.height = 2000

    # Dashboard-Index Parameter (für Mobile Initial-Load)
    dashboard_index = properties.get('dashboard_index', None)
    if dashboard_index is not None:
      if self.is_mobile:
        print(f"[multiframe] Mobile: Lade Dashboard {dashboard_index}")
        self.lade_iframe_mobile(dashboard_index)
      else:
        print(f"[multiframe] Desktop: Lade Dashboard {dashboard_index}")
        self.lade_und_zeige_iframe(dashboard_index)

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if index < 0 or index >= len(self.iframe_urls):        
      print("[multiframe] erstelle_iframe ",self.current_user['email'],f"Ungültiger Index: {index}")
      return

    url = self.iframe_urls[index]
    panel = self.panels[0] if self.is_mobile else self.panels[index]

    # Parameter für Supabase Key hinzufügen
    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
      print("(multiframe) erstelle_iframe: ",iframe_url)
    else:
      iframe_url = url

    # Vorheriges IFrame entfernen falls vorhanden
    jQuery(get_dom_node(panel)).empty()

    # IFrame erstellen mit expliziten Attributen
    height = "1000" if self.is_mobile else "1950"
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": height,
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

    if index < 0 or index >= len(self.iframe_urls):
      print(self.current_user['email']," ",f"Ungültiger Index: {index}")
      return

    # IMMER das alte Panel verstecken, BEVOR wir das neue zeigen
    if self.aktueller_index is not None and self.aktueller_index != index:
      self.panels[self.aktueller_index].visible = False

    # OPTIMIERUNG: Wenn bereits angezeigt, nichts tun
    if self.aktueller_index == index:
      return

    # IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      self.erstelle_iframe(index)

    # Gewünschtes Panel anzeigen
    self.panels[index].visible = True
    self.aktueller_index = index

    # Nach oben scrollen
    anvil.js.window.scrollTo(0, 0)
    
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

  def lade_restliche_iframes(self):
    """Lädt IFrames 1-10 im Hintergrund"""
    for i in range(1, len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
        print("[multiframe] lade_restliche_iframses erstelle iframe",i)

  def lade_iframe_mobile(self, index):
    """Einfaches IFrame laden für Mobile - nutzt nur Panel 0"""
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
  
    # Alte iframes entfernen
    jQuery(get_dom_node(panel)).find('iframe').remove()
    jQuery(get_dom_node(panel)).empty()
  
    # Neues iframe erstellen
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1000",
      "frameborder": "0",
      "scrolling": "no",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox": "allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    })
  
    iframe.appendTo(get_dom_node(panel))
    panel.visible = True
  
    print(f"[multiframe mobile] IFrame {index} geladen in Panel 0")
  
    # Nach oben scrollen
    anvil.js.window.scrollTo(0, 0)

