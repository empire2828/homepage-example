from ._anvil_designer import multiframeTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

class multiframe(multiframeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    user = users.get_user()
    if user and 'supabase_key' in user:
      self.supabase_key = user['supabase_key']
    else:
      self.supabase_key = ""
      print("Warnung: Kein supabase_key verfügbar")

    # Liste deiner 8 unterschiedlichen URLs
    self.iframe_urls = [
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF",          # Dashboard
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",    # Profitability
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_9euf3853td",    # Bookings
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_knw9h153td", # Cancellations
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_1idplf63td",     # Occupancy
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8hyzd253td",     # Lead Time
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_tilmy6zhtd", # Guest Insights
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_cc0slxgtud" # Detailed Bookings
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_9euf3853td",    # Long Trends
    ]

    # Panels für 8 IFrames - verwende das content_panel aus dem Designer
    self.panels = [
      self.looker_flow_panel_1,
      self.looker_flow_panel_2,
      self.looker_flow_panel_3,
      self.looker_flow_panel_4,
      self.looker_flow_panel_5,
      self.looker_flow_panel_6,
      self.looker_flow_panel_7,
      self.looker_flow_panel_8,
    ]

    #print(f"✅ Gefundene Panels im content_panel: {len(self.panels)}")

    # Status-Tracking welche IFrames bereits geladen wurden
    self.geladene_iframes = [False] * len(self.iframe_urls)

    # Aktuell sichtbarer Index
    self.aktueller_index = None

    # Initial: alle Panels unsichtbar
    for i, panel in enumerate(self.panels):
      panel.visible = False
      panel.height = 1850  # Explizite Höhe
      #print(f"Panel {i}: visible={panel.visible}, height={panel.height}")

    #print("🔧 multiframe mit content_panel initialisiert")

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    #print(f"🔨 Erstelle IFrame {index}...")
    if index < 0 or index >= len(self.iframe_urls):
      print(f"❌ Ungültiger Index: {index}")
      return

    url = self.iframe_urls[index]
    panel = self.panels[index]

    #print(f"📋 Panel {index}: {type(panel)}, visible={panel.visible}")

    # Parameter für Supabase Key hinzufügen
    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
    else:
      iframe_url = url

    #print(f"🌐 IFrame URL: {iframe_url[:80]}...")

    # Vorheriges IFrame entfernen falls vorhanden
    jQuery(get_dom_node(panel)).empty()

    # IFrame erstellen mit expliziten Attributen
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0",
      "style": "border: none; background: white;",
      "allow": "fullscreen",
      "loading": "lazy"
    })

    # IFrame zum Panel hinzufügen
    iframe.appendTo(get_dom_node(panel))

    # Als geladen markieren
    self.geladene_iframes[index] = True
    #print(f"✅ IFrame {index} erfolgreich geladen")

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    #print(f"\n🎯 lade_und_zeige_iframe({index}) aufgerufen")
    #print(f"   Aktueller Index: {self.aktueller_index}")

    if index < 0 or index >= len(self.iframe_urls):
      print(f"❌ Ungültiger Index: {index}")
      return

    # SCHRITT 1: Alle Panels verstecken
    #print("👀 Verstecke alle Panels...")
    for i, panel in enumerate(self.panels):
      if panel.visible:
        print(f"   Panel {i} war sichtbar -> verstecke")
      panel.visible = False

    # SCHRITT 2: IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      #print(f"📥 IFrame {index} wird erstmalig geladen...")
      self.erstelle_iframe(index)
    else:
      print(f"♻️ IFrame {index} bereits geladen")

    # SCHRITT 3: Gewünschtes Panel anzeigen
    #print(f"🔛 Zeige Panel {index}...")
    self.panels[index].visible = True
    self.aktueller_index = index

    # SCHRITT 4: Bestätigung
    #print(f"✅ Panel {index} Status: visible={self.panels[index].visible}")

    # Debug: Finale Status-Ausgabe
    #sichtbare_panels = [i for i, p in enumerate(self.panels) if p.visible]
    #print(f"📊 Sichtbare Panels: {sichtbare_panels}")

  # Backward compatibility - alte Methode
  # def setze_sichtbares_iframe(self, index):
  #  """Wrapper für Rückwärtskompatibilität"""
  #  print(f"🔄 setze_sichtbares_iframe({index}) -> lade_und_zeige_iframe")
  #  self.lade_und_zeige_iframe(index)

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames ohne sie zu entladen"""
    print("🙈 Verstecke alle IFrames...")
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
    #print("📦 Lade alle IFrames im Voraus...")
    for i in range(len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)
    #print("✅ Alle IFrames geladen")

  #def debug_info(self):
  #  """Gibt Debug-Informationen aus"""
  #  print("\n=== 🔍 MULTIFRAME DEBUG INFO ===")
  #  print(f"content_panel vorhanden: {hasattr(self, 'content_panel')}")
  #  print(f"Panels: {len(self.panels)}")
  #  print(f"URLs: {len(self.iframe_urls)}")
  #  print(f"Aktueller Index: {self.aktueller_index}")

    #for i, panel in enumerate(self.panels):
      #status = "✅ SICHTBAR" if panel.visible else "❌ versteckt"
      #geladen = "✅ geladen" if self.geladene_iframes[i] else "❌ nicht geladen"
      #print(f"Panel {i}: {status}, {geladen}, height={getattr(panel, 'height', 'unknown')}")
    #print("================================\n")

  # Event Handler für fehlende Buttons (um Warnungen zu vermeiden)
  def channel_manager_connect_button_click(self, **event_args):
    """Platzhalter für fehlenden Event Handler"""
    pass

  def dashboard_upgrade_button_click(self, **event_args):
    """Platzhalter für fehlenden Event Handler"""
    pass