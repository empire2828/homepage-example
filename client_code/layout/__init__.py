from ._anvil_designer import layoutTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import m3.components as m3

class layout(layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    password_reset_item=m3.MenuItem(text="Passwort rücksetzen")
    logout_item = m3.MenuItem(text="Ausloggen")
    subscription_admin_item=m3.MenuItem(text="Abo verwalten (via Stripe)")
    subscription_admin_item.set_event_handler("click",self.subscription_admin_link_click)
    password_reset_item.set_event_handler("click",self.password_reset_link_click)
    logout_item.set_event_handler("click", self.logout_link_click)
    self.user_icon_button_menu.menu_items = [password_reset_item,subscription_admin_item,logout_item]
  
  def dashboard_link_click(self, **event_args):
   self.reset_links()
   open_form('dashboard')
   self.dashboard_link.role='selected'
  
  def guestscreen_link_click(self, **event_args):
    self.reset_links()
    open_form('guestscreen')
    self.guestscreen_link.role='selected'

  
  def reset_links(self, **event_args):
    self.dashboard_link.role = ''
    self.guestscreen_link.role = ''
    self.channel_manager_connect_link.role = '' 
    self.upgrade_link.role = ''

  def upgrade_link_click(self, **event_args):
    self.reset_links()
    self.upgrade_link.role='selected'
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
        else:
          alert('Abo bereits vorhanden.')
    except Exception as e:
        alert(f'Ein Fehler ist aufgetreten: {e}')
    #identisch zu in Dashboard zu pflegen!

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
        if user['subscription'] is None:
            self.subscription_body.text = 'Trial subscription'
        else:
            self.subscription_body.text = user['subscription']

  def help_icon_button_click(self, **event_args):
    open_form('help')
    pass

  def password_reset_link_click(self, **event_args):
    alert('Sie erhalten eine eMail zum Zurücksetzen des Passwortes. Bitte haben Sie ein klein wenig Geduld.')
    anvil.server.call('send_password_reset_email')
    pass

  def subscription_admin_link_click(self, **event_args):
    alert('Sie werden jetzt auf die Seite unseres Zahlungsanbieters Stripe weitergeleitet.')
    anvil.js.window.open("https://billing.stripe.com/p/login/test_3csg0Lcbpf4i8005kk", "_blank")
    pass