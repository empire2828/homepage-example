from ._anvil_designer import homepageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class homepage(homepageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #anvil.server.call('server_wake_up')
    # Any code you write here will run before the form opens.

  def login_button_click(self, **event_args):
   user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=False, allow_remembered=True)
   if user:
    open_form('dashboard')
    pass

  def testen_button_click(self, **event_args):
    result = alert(
    content="Bitte bestätigen Sie, dass Sie als Ferienhaus- oder Ferienwohnungsvermieter ein berechtigtes Interesse an zusätzlichen Prüfungen Ihrer Gästedaten zu haben, um so Ihr Eigentüm besser zu schützen. Dieser Service richtet sich ausschließlich an Vermieter.",
    title="Bestätigung berechtigtes Interesse nach DSVGO",
    large=True,
    buttons=[
        ("Yes", "YES"),
        ("No", "NO"),
    ]
    )
    if result=='YES':
      user = anvil.users.signup_with_form(allow_cancel=True)
      if user:
        open_form('dashboard')
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
