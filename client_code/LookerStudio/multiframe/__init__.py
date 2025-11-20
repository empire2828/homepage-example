from ._anvil_designer import multiframeTemplate
from anvil import *
from routing import router
import m3.components as m3
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import datetime
import json

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/3a999ac2-c008-44c2-8cbb-3f1847c37211/page/"
  #share unlisted anyone can listen, embed ohne menu
  # Lodginia 1.0.08
  
  def __init__(self, **properties):
    self.init_components(**properties)
    self.supabase_key= ""
    user = users.get_user()    
    print('User Logged in: ',user['email'])
    #anvil.server.call('log',"user logged in",user['email'],"multiframe")

    user_has_subscription= anvil.server.call('get_user_has_subscription_for_email',user['email'])

    if user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.channel_manager_connect_button.visible = True
    else:
      is_user_below_request_count= anvil.server.call('is_user_below_request_count',user['email'])
      if user_has_subscription is False and is_user_below_request_count is False:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True
        self.pms_need_to_connect_text.visible = False
        self.channel_manager_connect_button.visible = False
    if user_has_subscription and user['smoobu_api_key'] is not None:      
      if user and 'supabase_key' in user:
        self.supabase_key = user['supabase_key']
        self.content_panel.visible = True
      else:
        self.supabase_key = ""
        print(user['email']," Warnung: Kein supabase_key verfügbar")      
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
      panel.height = 2300  # Explizite Höhe

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    user = users.get_user()
    if index < 0 or index >= len(self.iframe_urls):        
      print(user['email'],f"Ungültiger Index: {index}")
      return

    url = self.iframe_urls[index]
    panel = self.panels[index]

    # Parameter für Supabase Key hinzufügen
    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
      print(user['email']," ",iframe_url)
    else:
      iframe_url = url

     # Vorheriges IFrame entfernen falls vorhanden
    jQuery(get_dom_node(panel)).empty()

    # IFrame erstellen mit expliziten Attributen
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "2300px",
      "frameborder": "0",
      "style": "border: none; background: white;",
      "allow": "fullscreen; storage-access",
      "loading": "lazy",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox":"allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    })

    # IFrame zum Panel hinzufügen
    iframe.appendTo(get_dom_node(panel))

    # Als geladen markieren
    self.geladene_iframes[index] = True

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    if index < 0 or index >= len(self.iframe_urls):
      user = users.get_user()   
      print(user['email']," ",f"Ungültiger Index: {index}")
      return

    # SCHRITT 1: Alle Panels verstecken
    for i, panel in enumerate(self.panels):
      #if panel.visible:
      #  print(f"Panel {i} war sichtbar -> verstecke")
      panel.visible = False

    # SCHRITT 2: IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      #print(f"IFrame {index} wird erstmalig geladen...")
      self.erstelle_iframe(index)
    else:
      print(user['email']," ",f"IFrame {index} bereits geladen")

    # SCHRITT 3: Gewünschtes Panel anzeigen
    self.panels[index].visible = True
    self.aktueller_index = index

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames ohne sie zu entladen"""
    print("Verstecke alle IFrames...")
    for i, panel in enumerate(self.panels):
      panel.visible = False
      #print(f"   Panel {i} versteckt")
    self.aktueller_index = None

  def ist_geladen(self, index):
    """Prüft ob IFrame bereits geladen ist"""
    if index < 0 or index >= len(self.geladene_iframes):
      return False
    return self.geladene_iframes[index]

  def lade_alle_iframes(self):
    """Lädt alle IFrames im Voraus (falls gewünscht für bessere Performance)"""
    #print("Lade alle IFrames im Voraus...")
    for i in range(len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
    #print("Alle IFrames geladen")

  # Event Handler für fehlende Buttons (um Warnungen zu vermeiden)
  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
    pass
