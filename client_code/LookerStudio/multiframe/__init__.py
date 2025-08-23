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
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td",
      "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/p_8l5lnc13td"
      # ... bis URL8
    ]

    # Panels für 8 IFrames im Editor anlegen (z. B. flow_panel_1 ... flow_panel_8)
    panels = [
      self.looker_flow_panel_1,
      self.looker_flow_panel_2,
      self.looker_flow_panel_3,
      self.looker_flow_panel_4,
      self.looker_flow_panel_5,
      self.looker_flow_panel_6,
      self.looker_flow_panel_7,
      self.looker_flow_panel_8,
    ]
    self.panels = panels

    # Initial: alle unsichtbar
    for panel in panels:
      panel.visible = True

    # alle IFrames einmalig hineinlegen (das ist performant, da sie im DOM bleiben)
    for url, panel in zip(self.iframe_urls, panels):
      params = {"supabase_key_url": supabase_key}
      encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
      iframe_url = url + encoded_params
      iframe = jQuery("<iframe>").attr({
        "src": iframe_url,
        "width": "100%",
        "height": "1800px",
        "frameborder": "0"
      })
      print(panel)
      iframe.appendTo(get_dom_node(panel))

  # zentrale Steuerfunktion:
  def setze_sichtbares_iframe(self, index):
    # Alle verstecken, das gewünschte sichtbar machen
    for i, panel in enumerate(self.panels):
      panel.visible = (i == index)
