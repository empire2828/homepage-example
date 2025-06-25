from ._anvil_designer import settingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .ChangeName import ChangeName
from .ChangeEmail import ChangeEmail
from .DeleteAccountAlert import DeleteAccountAlert

class settings(settingsTemplate):
  def __init__(self, **properties):
    self.user = anvil.users.get_user()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    # Hier kommt dein Code hin, der beim Anzeigen der Form ausgeführt werden soll
    pass
  
  def change_name_link_click(self, **event_args):
    new_name = alert(ChangeName(item=self.user["name"]), title="Change name", buttons=None, dismissible=True, large=True)
    if new_name:
      self.user = anvil.server.call('change_name', new_name)
      self.refresh_data_bindings()

  def change_email_link_click(self, **event_args):
    new_email = alert(ChangeEmail(item=self.user["email"]), title="Change email", buttons=None, dismissible=True, large=True)
    if new_email:
      self.user = anvil.server.call('change_email', new_email)
      self.refresh_data_bindings()

  def reset_password_link_click(self, **event_args):
    if confirm("Resetting your password will send a reset email to your inbox and log you out. Do you want to continue?"):
      anvil.users.send_password_reset_email(self.user["email"])
      alert("A password reset email has been sent to your inbox.", title="Password reset email sent")
      anvil.users.logout()
      open_form("LoginPage")

  #def delete_account_link_click(self, **event_args):
  #  if alert(DeleteAccountAlert(), buttons=None, large=True):
  #   anvil.server.call('delete_user')
  #    anvil.users.logout()
  #    open_form('LoginPage')

  #def name_change_link_click(self, **event_args):
  #  open_form('AccountManagement.ChangeName')
  #  pass

  #def email_change_link_click(self, **event_args):
  #  open_form('AccountManagement.ChangeEmail')
  #  pass

  def account_delete_link_click(self, **event_args):
    open_form('AccountManagement.DeleteAccountAlert')
    pass

  def password_reset_link_click(self, **event_args):
    open_form('AccountManagement.reset_password')
    pass

  def logout_navigation_link_click(self, **event_args):
    result = alert(
          content="Do you want to logout?",
          title="Log out",
          buttons=[
            ("Yes", "YES"),
            ("No", "NO"),
          ])
    if result == "YES":
      anvil.users.logout()
      open_form('homepage')
      pass

  def subscription_management_navigation_link_click(self, **event_args):
    alert('Du wirst jetzt auf die Seite unseres Zahlungsanbieters Stripe weitergeleitet.')
    anvil.js.window.open("https://billing.stripe.com/p/login/7sIeW3aAjf8CgIodQQ", "_blank")
    #link ist unter: https://dashboard.stripe.com/settings/billing/portal
    pass

