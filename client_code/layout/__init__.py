from ._anvil_designer import layoutTemplate
from anvil import *
import anvil.users
import anvil.server
import m3.components as m3
import time
import anvil.js

class layout(layoutTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    password_reset_item=m3.MenuItem(text="Passwort rücksetzen")
    logout_item = m3.MenuItem(text="Ausloggen")
    subscription_admin_item=m3.MenuItem(text="Abo verwalten (via Stripe)")
    subscription_admin_item.set_event_handler("click",self.subscription_admin_link_click)
    password_reset_item.set_event_handler("click",self.password_reset_link_click)
    logout_item.set_event_handler("click", self.logout_link_click)
    self.user_icon_button_menu.menu_items = [password_reset_item,subscription_admin_item,logout_item]
  
  def reset_links(self, **event_args):
    self.analytics_menu_item.background_color = ''
    self.channel_manager_connect_menu_item.background_color = '' 
    self.upgrade_menu_item.background_color = ''
    self.admin_menu_item.background_color = ''

  def upgrade_menu_item_click(self, **event_args):
    self.reset_links()
    anvil.js.window.scrollTo(0, 0)
    self.upgrade_menu_item.background_color='theme:Secondary Container'
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

  def channel_manager_connect_menu_item_click(self, **event_args):
    self.reset_links()
    anvil.js.window.scrollTo(0, 0)
    open_form('channel_manager_connect')
    self.channel_manager_connect_menu_item.background_color='theme:Secondary Container'
    pass

  def form_show(self, **event_args):
    user = anvil.users.get_user()
    if user is None:
      self.subscription_body.text = 'Not logged in'
    elif user.get('subscription') is None:
      self.subscription_body.text = 'Trial subscription'
    else:
      self.subscription_body.text = user['subscription']
      if user.get('admin') is True:
        self.admin_menu_item.visible= True

  def help_icon_button_click(self, **event_args):
    self.reset_links()
    open_form('help')
    pass

  def password_reset_link_click(self, **event_args):
    alert('Du erhältst eine eMail zum Zurücksetzen des Passwortes. Bitte habe ein klein wenig Geduld.')
    anvil.server.call('send_password_reset_email')
    pass

  def subscription_admin_link_click(self, **event_args):
    alert('Du wirst jetzt auf die Seite unseres Zahlungsanbieters Stripe weitergeleitet.')
    anvil.js.window.open("https://billing.stripe.com/p/login/7sIeW3aAjf8CgIodQQ", "_blank")
    #link ist unter: https://dashboard.stripe.com/settings/billing/portal
    pass

  def admin_menu_item_click(self, **event_args):
    self.reset_links()
    self.admin_menu_item.background_color='theme:Secondary Container'
    open_form('Admin')
    pass

  def analytics_menu_item_click(self, **event_args):
    self.reset_links()
    self.analytics_menu_item.background_color='theme:Secondary Container'
    open_form('Analytics')
    pass


 
