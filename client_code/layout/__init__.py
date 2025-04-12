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
    has_subscription = anvil.server.call_s('get_user_has_subscription')
    if not has_subscription:
        open_form('StripePricing')
    else:
      alert('Abo ist bereits upgegraded')

  def logout_link_click(self, **event_args):
      anvil.users.logout()
      open_form('homepage')
  pass

  def channel_manager_connect_link_click(self, **event_args):
    self.reset_links()
    open_form('channel_manager_connect')
    self.channel_manager_connect_link.role='selected'
    pass

  def form_show(self, **event_args):
    has_subscription = anvil.server.call_s('get_user_has_subscription')
    if has_subscription:
      self.subscription_body.text="Pro-Abo"
    else:
      self.subscription_body.text="Basis-Abo"
    pass
