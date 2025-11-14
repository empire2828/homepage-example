from ._anvil_designer import home_deTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.users
import anvil.js

class home_de(home_deTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
      anvil.server.call("create_supabase_key")
      anvil.server.call("send_registration_notification", user["email"])
      # Layout Template öffnen
      layout_form = open_form("layout_template")
      # Dashboard automatisch laden
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
    pass

  def impressum_link_click(self, **event_args):
    open_form("impressum")
    pass

  #def home_link_click(self, **event_args):
  #  open_form("home_start")
  #  pass

  def pricing_link_click(self, **event_args):
    self.pricing_label.scroll_into_view()
    pass

  def data_protection_link_click(self, **event_args):
    open_form("data_protection")
    pass
