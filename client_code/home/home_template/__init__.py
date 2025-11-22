from ._anvil_designer import home_templateTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.server
import anvil.google.auth
#, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
from ... import globals

class home_template(home_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.user_locale = anvil.js.window.navigator.language

    # Any code you write here will run before the form opens.

  def login_button_click(self, **event_args):
    user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=False, allow_remembered=True)
    if user:
      # Layout Template öffnen
      globals.current_user = user
      layout_form = open_form('layout_template')

      # Dashboard automatisch laden
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard

      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
   
      if globals.current_user is not None:
        globals.user_has_subscription = anvil.server.call('get_user_has_subscription_for_email',globals.current_user)
        if globals.user_has_subscription is False:
          layout_form.upgrade_navigation_link.badge = True
          globals.request_count = anvil.server.call('get_request_count')
          layout_form.upgrade_navigation_link.badge_count = globals.request_count
    pass

  def blog_button_click(self, **event_args):
    if self.user_locale.lower().startswith("de"):
      open_form('blog.blog_de')
      #router.navigate('/blog_de')
    else:
      open_form('blog.blog_en')
      #router.navigate('/blog_de')
    pass

  def lodginia_button_click(self, **event_args):
    open_form("home.home_start")
    pass

  def about_us_button_click(self, **event_args):
    if self.user_locale.lower().startswith("de"):
      open_form('home.about_us_de')
    else:
      open_form('home.about_us_en')
    pass