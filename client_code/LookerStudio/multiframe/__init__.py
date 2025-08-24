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
    supabase_key = user['supabase_key']

    # Liste deiner 8 unterschiedlichen URLs
    self.iframe_urls = [
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF",          # Dashboard
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",    # Profitability
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_long_trends",    # Long Trends
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_cancellations", # Cancellations
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_occupancy",     # Occupancy
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_lead_time",     # Lead Time
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_guest_insights", # Guest Insights
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_detailed_bookings" # Detailed Bookings
    ]

    # Panels für 8 IFrames
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

    # Status-Tracking welche IFrames bereits geladen wurden
    self.geladene_iframes = [False] * len(self.iframe_urls)

    # Aktuell sichtbarer Index
    self.aktueller_index = None

    # Initial: alle Panels unsichtbar
    for panel in self.panels:
      panel.visible = False

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if index < 0 or index >= len(self.iframe_urls):
      return

    url = self.iframe_urls[index]
    panel = self.panels[index]

    # Parameter für Supabase Key hinzufügen
    params = {"supabase_key_url": supabase_key}
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = url + encoded_params

    # IFrame erstellen
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })

    # IFrame zum Panel hinzufügen
    iframe.appendTo(get_dom_node(panel))

    # Als geladen markieren
    self.geladene_iframes[index] = True
    print(f"IFrame {index} geladen")

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    if index < 0 or index >= len(self.iframe_urls):
      return

    # Aktuelles IFrame verstecken (falls vorhanden)
    if self.aktueller_index is not None:
      self.panels[self.aktueller_index].visible = False

    # IFrame laden falls noch nicht geschehen
    if not self.geladene_iframes[index]:
      self.erstelle_iframe(index)

    # Gewünschtes IFrame anzeigen
    self.panels[index].visible = True
    self.aktueller_index = index
    print(f"IFrame {index} angezeigt")

  # Backward compatibility - alte Methode
  def setze_sichtbares_iframe(self, index):
    """Wrapper für Rückwärtskompatibilität"""
    self.lade_und_zeige_iframe(index)

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames ohne sie zu entladen"""
    for panel in self.panels:
      panel.visible = False
    self.aktueller_index = None

  def ist_geladen(self, index):
    """Prüft ob IFrame bereits geladen ist"""
    if index < 0 or index >= len(self.geladene_iframes):
      return False
    return self.geladene_iframes[index]

  def lade_alle_iframes(self):
    """Lädt alle IFrames im Voraus (falls gewünscht für bessere Performance)"""
    for i in range(len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        self.erstelle_iframe(i)