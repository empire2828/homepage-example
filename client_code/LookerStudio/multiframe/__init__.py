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
    self.supabase_key = ""  
    self.current_user = globals.current_user
    request_count = int(globals.request_count)

    is_user_below_request_count = request_count <= 20

    if self.current_user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      self.channel_manager_connect_button.visible = True
    elif globals.user_has_subscription is False and not is_user_below_request_count:
      self.dashboard_upgrade_needed_text_1.visible = True
      self.dashboard_upgrade_needed_text_2.visible = True
      self.dashboard_upgrade_button.visible = True

    if (is_user_below_request_count or globals.user_has_subscription) and self.current_user['smoobu_api_key'] is not None:      
      if 'supabase_key' in self.current_user and self.current_user['supabase_key']:
        self.supabase_key = self.current_user['supabase_key']
        self.content_panel.visible = True
      else:
        print(f"{self.current_user['email']} - Warnung: Kein supabase_key verfügbar")

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

    self.geladene_iframes = [False] * len(self.iframe_urls)
    self.aktueller_index = None

    for panel in self.panels:
      panel.visible = False
      panel.height = 2300

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if not (0 <= index < len(self.iframe_urls)):
      return

    url = self.iframe_urls[index]
    panel = self.panels[index]

    if self.supabase_key:
      params = {"supabase_key_url": self.supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
    else:
      iframe_url = url

    jQuery(get_dom_node(panel)).empty()

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "2300px",
      "frameborder": "0",
      "style": "border: none; background: white;",
      "allow": "fullscreen; storage-access",
      "loading": "lazy",
      "referrerpolicy": "origin-when-cross-origin",
      "sandbox": "allow-scripts allow-same-origin allow-storage-access-by-user-activation"
    })

    iframe.appendTo(get_dom_node(panel))
    self.geladene_iframes[index] = True

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls noch nicht geladen und zeigt es an"""
    if not (0 <= index < len(self.iframe_urls)):
      return

    if self.aktueller_index == index:
      return

    if self.aktueller_index is not None:
      self.panels[self.aktueller_index].visible = False

    if not self.geladene_iframes[index]:
      self.erstelle_iframe(index)

    self.panels[index].visible = True
    self.aktueller_index = index

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames ohne sie zu entladen"""
    for panel in self.panels:
      panel.visible = False
    self.aktueller_index = None

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')

