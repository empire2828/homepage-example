from ._anvil_designer import home_templateTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.google.auth
import anvil.users
from ... import globals
import datetime

class home_template(home_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.user_locale = anvil.js.window.navigator.language

  def login_button_click(self, **event_args):
    self.user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=False, allow_remembered=True)
    if self.user:
      globals.current_user = self.user      
      globals.user_has_subscription = anvil.server.call_s('get_user_has_subscription_for_email', self.user)

      # Request count
      last_login = self.user.get('last_login', None)
      must_refresh = False
      globals.request_count = 0

      if last_login is not None:
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        delta = now_dt - last_login
        if delta.total_seconds() < 24 * 3600:
          must_refresh = True

      if must_refresh:
        globals.request_count = anvil.server.call_s('get_request_count')

      # Öffne layout_template NUR EINMAL
      layout_form = open_form('layout_template')

      # Speichere Referenz in globals für späteren Zugriff
      globals.layout_form = layout_form

      # Dashboard anzeigen (ohne open_form!)
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
      layout_form.show_multiframe(0)  # Zeigt Dashboard


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