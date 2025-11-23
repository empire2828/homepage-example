from ._anvil_designer import stly_deTemplate
from anvil import *
import anvil.server
from routing import router
import m3.components as m3
import anvil.google.auth, anvil.google.drive
import anvil.users
from anvil.tables import app_tables
from ... import globals

class stly_de(stly_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

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
