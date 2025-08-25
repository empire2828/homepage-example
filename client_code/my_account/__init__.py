from ._anvil_designer import my_accountTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .ChangeName import ChangeName
from .ChangeEmail import ChangeEmail
from .DeleteAccountAlert import DeleteAccountAlert

class my_account(my_accountTemplate):
  def __init__(self, **properties):
    self.user = anvil.users.get_user()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    user = anvil.users.get_user()
    if user is None:
      self.subscription_body.text = 'Not logged in'
    else:
      if user.get('subscription') is None:
        self.subscription_body.text = 'Trial subscription'
      else:
        self.subscription_body.text = user['subscription']
        if user.get('admin') is True:
          self.admin_navigation_link.visible= True
        self.email_body.text = user['email']
        user_parameters = anvil.server.call_s('get_user_parameter')
        if user_parameters:
          self.std_cleaning_fee_text_box.text = str(user_parameters.get('std_cleaning_fee', ''))
          self.std_linen_fee_text_box.text = str(user_parameters.get('std_linen_fee', ''))
          self.use_own_std_fees_checkbox.checked = user_parameters.get('use_own_std_fees', False)
        
        # Load used channels for the user from Supabase std_commission
        # Load channels and commissions from Supabase
        user_email = user.get('email')
        channel_data = anvil.server.call('get_user_channels_from_std_commission', user_email)
      
        # Populate dropdowns and textboxes for up to 5 channels
        for i in range(1, 10):
          d = getattr(self, f'channel{i}_dropdown_menu')
          t = getattr(self, f'channel{i}_text_box')
          name = channel_data[i-1]['channel_name'] if i-1 < len(channel_data) else ''
          comm = channel_data[i-1]['channel_commission'] if i-1 < len(channel_data) else ''
          d.items = [c['channel_name'] for c in channel_data]
          d.selected_value = name or None
          t.text = str(comm) if comm else ''

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
    open_form('my_account.DeleteAccountAlert')
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
      open_form('homepage', force= True)
      pass

  def subscription_management_navigation_link_click(self, **event_args):
    alert('Du wirst jetzt auf die Seite unseres Zahlungsanbieters Stripe weitergeleitet.')
    anvil.js.window.open("https://billing.stripe.com/p/login/7sIeW3aAjf8CgIodQQ", "_blank")
    #link ist unter: https://dashboard.stripe.com/settings/billing/portal
    pass

  def connect_navigation_link_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def save_button_click(self, **event_args):
    std_cleaning_fee=self.std_cleaning_fee_text_box.text
    std_linen_fee=self.std_linen_fee_text_box.text
    use_own_std_fees=self.use_own_std_fees_checkbox.checked
    anvil.server.call('save_user_parameter',std_cleaning_fee, std_linen_fee,use_own_std_fees)
    channel_name= self.channel1_dropdown_menu.selected_value
    channel_commission= self.channel1_text_box.text
    anvil.server.call('save_std_commission', channel_name, channel_commission)
    channel_name= self.channel2_dropdown_menu.selected_value
    channel_commission= self.channel2_text_box.text
    anvil.server.call('save_std_commission', channel_name, channel_commission)
    channel_name= self.channel3_dropdown_menu.selected_value
    channel_commission= self.channel3_text_box.text
    anvil.server.call('save_std_commission', channel_name, channel_commission)
    channel_name= self.channel4_dropdown_menu.selected_value
    channel_commission= self.channel4_text_box.text
    anvil.server.call('save_std_commission', channel_name, channel_commission)
    channel_name= self.channel5_dropdown_menu.selected_value
    channel_commission= self.channel5_text_box.text
    anvil.server.call('save_std_commission', channel_name, channel_commission)
    pass

  def upgrade_navigation_link_link_click(self, **event_args):
    open_form('upgrade')
    pass

  def reset_password_navigation_link_click(self, **event_args):
    open_form('my_account.reset_password')
    pass

  

