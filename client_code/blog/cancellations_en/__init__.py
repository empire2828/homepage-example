from ._anvil_designer import cancellations_enTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.server
import anvil.google.auth, anvil.google.drive
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from plotly import graph_objects as go
from ... import globals

class cancellations_en(cancellations_enTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
      anvil.server.call("create_supabase_key")
      anvil.server.call("send_registration_notification", user["email"])
      # Layout Template öffnen
      globals.current_user = user
      globals.request_count = 0
      globals.user_has_subscription= False
      layout_form = open_form("layout_template")
      # Dashboard automatisch laden
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True   
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
      # Navigation Link als aktiv markieren