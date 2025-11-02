from ._anvil_designer import homepageTemplate
from anvil import *
import anvil.server
import anvil.users

class homepage(homepageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def login_button_click(self, **event_args):
    user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=False, allow_remembered=True)
    if user:
      # Layout Template öffnen
      layout_form = open_form('layout_template')
  
      # Dashboard automatisch laden
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
  
      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
    pass

  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
      anvil.server.call('create_supabase_key')
      anvil.server.call('send_registration_notification', user['email'])
      # Layout Template öffnen
      layout_form = open_form('layout_template')
      # Dashboard automatisch laden
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
    pass

  def impressum_link_click(self, **event_args):
    open_form('impressum')
    pass

  def data_protection_link_click(self, **event_args):
    open_form('data_protection')
    pass

  def home_link_click(self, **event_args):
    open_form('homepage')
    pass

  def pricing_link_click(self, **event_args):
    self.pricing_label.scroll_into_view()
    pass


