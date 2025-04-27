from ._anvil_designer import layoutTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

class layout(layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def dashboard_link_click(self, **event_args):
   self.reset_links()
   open_form('dashboard')
   self.dashboard_link.role='selected'
  
  def guestscreen_link_click(self, **event_args):
    self.reset_links()
    open_form('guestscreen')
    self.guestscreen_link.role='selected'

  def accountmanagement_link_click(self, **event_args):
    self.reset_links()
    open_form('AccountManagement')
    self.accountmanagement_link.role='selected'
    
  def reset_links(self, **event_args):
    self.dashboard_link.role = ''
    self.guestscreen_link.role = ''
    self.channel_manager_connect_link.role = ''  
    self.accountmanagement_link.role = ''
    self.upgrade_link.role = ''

  def upgrade_link_click(self, **event_args):
    try:
        user = anvil.users.get_user()
        if not user:
            alert('Kein Benutzer angemeldet')
            return

        subscription = user.get('subscription')
        apartment_count = user.get('apartment_count', 0) or 1

        if subscription != 'Subscription' and apartment_count < 4:
            open_form('StripePricing')
        elif subscription != 'Pro-Subscription' and apartment_count > 3:
            open_form('StripePricing_pro')
    except Exception as e:
        alert(f'Ein Fehler ist aufgetreten: {e}')

  def logout_link_click(self, **event_args):
      result= alert(
        content="Wollen Sie sich ausloggen?",
        title="Log off",
        buttons=[
        ("Yes", "YES"),
        ("No", "NO"),
      ])
      if result=="YES":
        anvil.users.logout()
        open_form('homepage')
      pass

  def channel_manager_connect_link_click(self, **event_args):
    self.reset_links()
    open_form('channel_manager_connect')
    self.channel_manager_connect_link.role='selected'
    pass

  def form_show(self, **event_args):
    user = anvil.users.get_user()
    if user is not None:
        if user['subscription'] == "Subscription":
            self.subscription_body.text = "Abo"
        elif user['subscription'] == "Pro-Subscription":
            self.subscription_body.text = "Pro- Abo"
        elif user['subscription'] is None:
            self.subscription_body.text = "Test- Abo"
        else:
            self.subscription_body.text = "Abo abgelaufen"
    else:
        self.subscription_body.text = "No User logged in"
