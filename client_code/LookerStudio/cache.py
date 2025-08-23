import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Globale Cache-Variablen (außerhalb der Klasse)
_iframe_cache = {}

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # ... rest des Codes bleibt gleich

  def init_iframe(self, supabase_key):
    cache_key = f"looker_iframe_{supabase_key}"

    # Prüfen, ob iframe bereits im globalen Cache vorhanden ist
    if cache_key in _iframe_cache:
      print("Lade iframe aus globalem Cache")
      get_dom_node(self.looker_flow_panel).innerHTML = ""
      _iframe_cache[cache_key].appendTo(get_dom_node(self.looker_flow_panel))
      return

    # iframe zum ersten Mal laden
    print("Lade iframe zum ersten Mal")
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    params = {"supabase_key_url": supabase_key}    

    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"

    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "1800px",
      "frameborder": "0"
    })

    iframe.appendTo(get_dom_node(self.looker_flow_panel))

    # iframe im globalen Cache speichern
    _iframe_cache[cache_key] = iframe
