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

    # Cache User-Daten
    self.current_user = globals.current_user
    self.supabase_key = self.current_user.get('supabase_key', '')
    request_count = int(globals.request_count)

    is_user_below_request_count = request_count <= 20
    has_subscription = globals.user_has_subscription
    has_api_key = self.current_user.get('smoobu_api_key') is not None

    # Sichtbarkeit
    self.pms_need_to_connect_text.visible = not has_api_key
    self.channel_manager_connect_button.visible = not has_api_key

    needs_upgrade = not has_subscription and not is_user_below_request_count
    self.dashboard_upgrade_needed_text_1.visible = needs_upgrade
    self.dashboard_upgrade_needed_text_2.visible = needs_upgrade
    self.dashboard_upgrade_button.visible = needs_upgrade

    self.content_panel.visible = (is_user_below_request_count or has_subscription) and has_api_key

    # IFrame URLs
    page_ids = [
      "qmCOF", "p_frni7wm2vd", "p_8l5lnc13td", "p_9euf3853td", 
      "p_knw9h153td", "p_1idplf63td", "p_8hyzd253td", "p_tilmy6zhtd",
      "p_4dt5tycuud", "p_cc0slxgtud", "p_396qlut0wd",
    ]

    self.iframe_urls = [f"{self.Locker_Version}{pid}" for pid in page_ids]

    self.panels = [
      self.looker_flow_panel_1, self.looker_flow_panel_2,
      self.looker_flow_panel_3, self.looker_flow_panel_4,
      self.looker_flow_panel_5, self.looker_flow_panel_6,
      self.looker_flow_panel_7, self.looker_flow_panel_8,
      self.looker_flow_panel_9, self.looker_flow_panel_10,
      self.looker_flow_panel_11,
    ]

    # Cache für jQuery DOM nodes - WICHTIG für Performance!
    self._panel_nodes = [get_dom_node(panel) for panel in self.panels]

    self.geladene_iframes = [False] * len(self.iframe_urls)
    self.aktueller_index = None

    # Panels initial konfigurieren
    for panel in self.panels:
      panel.visible = False
      panel.height = 2300

  def _build_iframe_url(self, base_url):
    """Baut die finale IFrame URL mit Parametern"""
    if not self.supabase_key:
      return base_url

    params = {"supabase_key_url": self.supabase_key}
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    return base_url + encoded_params

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if not (0 <= index < len(self.iframe_urls)):
      return

    url = self._build_iframe_url(self.iframe_urls[index])

    # Nutze gecachten DOM node
    panel_node = self._panel_nodes[index]
    jQuery(panel_node).empty()

    # IFrame-Attribute
    iframe_attrs = {
      "src": url,
      "width": "100%",
      "height": "2300px",
      "frameborder": "0",
      "style": "border: none; background: white;",
      "allow": "fullscreen; storage-access",
      "loading": "lazy",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox": "allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    }

    jQuery("<iframe>").attr(iframe_attrs).appendTo(panel_node)
    self.geladene_iframes[index] = True

  def lade_und_zeige_iframe(self, index):
    """Optimierte Version - nur Sichtbarkeit ändern, kein Re-Rendering"""
    if not (0 <= index < len(self.iframe_urls)):
      return

    # Nur wenn tatsächlich gewechselt wird
    if self.aktueller_index == index:
      return  # Bereits angezeigt, nichts tun!

    # Vorheriges Panel verstecken (falls vorhanden)
    if self.aktueller_index is not None:
      self.panels[self.aktueller_index].visible = False

    # IFrame laden falls nötig
    if not self.geladene_iframes[index]:
      self.erstelle_iframe(index)

    # Neues Panel anzeigen
    self.panels[index].visible = True
    self.aktueller_index = index

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')
