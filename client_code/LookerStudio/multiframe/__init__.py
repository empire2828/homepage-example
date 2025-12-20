from ._anvil_designer import multiframeTemplate
from anvil import *
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json
from ... import globals

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/90173894-1f4b-4b83-9daf-a0b63eb59f3b/page/"

  # Konstante URLs - nur einmal definieren
  IFRAME_URLS = [
    "qmCOF",            # 0: Dashboard
    "p_frni7wm2vd",     # 1: Outlook
    "p_8l5lnc13td",     # 2: Profitability
    "p_9euf3853td",     # 3: Bookings
    "p_knw9h153td",     # 4: Cancellations
    "p_1idplf63td",     # 5: Occupancy
    "p_8hyzd253td",     # 6: Lead Time
    "p_tilmy6zhtd",     # 7: Guest Insights
    "p_4dt5tycuud",     # 8: Long Trends     
    "p_cc0slxgtud",     # 9: Detailed Bookings
    "p_396qlut0wd",     # 10: Knowledge hub
  ]

  def __init__(self, **properties):
    self.init_components(**properties)
    globals.current_multiframe_instance = self
    self.current_user = globals.current_user
    self.supabase_key = ""

    if self.current_user is None:
      print("[multiframe] Warnung: Kein current_user verfügbar")
      return

    if self.current_user.get('smoobu_api_key') is None:
      open_form('channel_manager_connect')
      return

    self.supabase_key = self.current_user.get('supabase_key', '')

    if not self.supabase_key:
      print(f"{self.current_user['email']} Warnung: Kein supabase_key verfügbar")
      return

    self.content_panel.visible = True
    print(f"[multiframe] init {self.current_user['email']}")

    # MOBILE: Nur 1 Panel
    # DESKTOP: Alle Panels
    self.is_mobile = anvil.js.window.innerWidth < 768

    self.panels = [self.looker_flow_panel_1]

    if not self.is_mobile:
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

    # Nur geladene IFrames tracken
    self.geladene_iframes = set()
    self.aktueller_index = None

    # Initial: alle Panels unsichtbar
    for panel in self.panels:
      panel.visible = False

  def _get_iframe_url(self, index):
    """Generiert die vollständige URL für einen Dashboard"""
    if index < 0 or index >= len(self.IFRAME_URLS):
      return None

    url = self.Locker_Version + self.IFRAME_URLS[index]

    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded = anvil.js.window.encodeURIComponent(json.dumps(params))
      return f"{url}?params={encoded}"

    return url

  def lade_und_zeige_iframe(self, index):
    """Optimiert: Lädt nur das benötigte IFrame"""

    if index < 0 or index >= len(self.IFRAME_URLS):
      print(f"{self.current_user['email']} Ungültiger Index: {index}")
      return

    # Altes Panel verstecken
    if self.aktueller_index is not None and self.aktueller_index != index:
      self.panels[self.aktueller_index].visible = False

    # Wenn bereits angezeigt, nicht neu laden
    if self.aktueller_index == index:
      return

    # IFrame erstellen/laden
    if index not in self.geladene_iframes:
      panel = self.panels[0] if self.is_mobile else self.panels[index]
      jQuery(get_dom_node(panel)).empty()

      url = self._get_iframe_url(index)
      if not url:
        return

      iframe = jQuery("<iframe>").attr({
        "src": url,
        "width": "100%",
        "frameborder": "0",
        "scrolling": "no",
        "loading": "lazy",
        "sandbox": "allow-scripts allow-same-origin allow-storage-access-by-user-activation"
      })

      if self.is_mobile:
        iframe.attr("height", "900")
      else:
        iframe.attr("height", "1950")

      iframe.appendTo(get_dom_node(panel))
      self.geladene_iframes.add(index)

    # Panel anzeigen
    self.panels[0 if self.is_mobile else index].visible = True
    self.aktueller_index = index

    anvil.js.window.scrollTo(0, 0)

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames"""
    for panel in self.panels:
      panel.visible = False
    self.aktueller_index = None
