from ._anvil_designer import my_accountTemplate
from anvil import *
import anvil.server
import anvil.users
from .. import globals

class my_account(my_accountTemplate):
  def __init__(self, **properties):
    self.user = anvil.users.get_user()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    self.my_account_heading.scroll_into_view(smooth=True)
    user = globals.current_user
  
    if user is None:
      self.subscription_body.text = 'Not logged in'
      return
  
    # Subscription / Admin
    self.subscription_body.text = user.get('subscription') or 'Free subscription'
    self.admin_navigation_link.visible = bool(user.get('admin'))
  
    # Request Count
    if user.get('request_count') is not None:
      self.request_count_body.text = user['request_count']
  
    # My-Account-Daten (Parameter + Channels) in EINEM Server-Call holen
    data = anvil.server.call('get_my_account_data', user['email'])
    user_parameters = data.get('params') or {}
    channel_data    = data.get('channels') or []
  
    # Parameter-Felder
    self.std_cleaning_fee_text_box.text = str(user_parameters.get('std_cleaning_fee') or '')
    self.std_linen_fee_text_box.text    = str(user_parameters.get('std_linen_fee') or '')
    self.use_own_std_fees_checkbox.checked = bool(user_parameters.get('use_own_std_fees'))
  
    # E-Mail
    self.email_body.text = user.get('email', '')
  
    # Channels nur einmal als Items-Liste berechnen
    items = [c['channel_name'] for c in channel_data]
  
    # Dropdowns/Textboxen über Schleife befüllen
    for i in range(1, 11):
      d = getattr(self, f'channel{i}_dropdown_menu')
      t = getattr(self, f'channel{i}_text_box')
      d.items = items
  
      if i-1 < len(channel_data):
        channel = channel_data[i-1]
        d.selected_value = channel.get('channel_name')
        t.text = str(channel.get('channel_commission') or '')
      else:
        d.selected_value = None
        t.text = ''

  #def change_name_link_click(self, **event_args):
  #  new_name = alert(ChangeName(item=self.user["name"]), title="Change name", buttons=None, dismissible=True, large=True)
  #  if new_name:
  #    self.user = anvil.server.call('change_name', new_name)
  #    self.refresh_data_bindings()

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
      open_form('home.home_start', force= True)
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
    # 1. User-Parameter speichern (1 Server-Call)
    std_cleaning_fee = self.std_cleaning_fee_text_box.text
    std_linen_fee = self.std_linen_fee_text_box.text
    use_own_std_fees = self.use_own_std_fees_checkbox.checked
    anvil.server.call('save_user_parameter', std_cleaning_fee, std_linen_fee, use_own_std_fees)
  
    # 2. Alle Channel-Daten sammeln
    channels_data = []
    for i in range(1, 11):  # Channel 1-10
      channel_dropdown = getattr(self, f'channel{i}_dropdown_menu')
      channel_textbox = getattr(self, f'channel{i}_text_box')
  
      channel_name = channel_dropdown.selected_value
      channel_commission = channel_textbox.text
  
      # Validierung: Nur wenn Name UND Commission vorhanden
      if channel_name and channel_commission and channel_commission != "None":
        channels_data.append({
          'name': channel_name,
          'commission': channel_commission
        })
  
      # 3. Alle Channels in EINEM Server-Call speichern
    if channels_data:
      anvil.server.call_s('save_std_commissions_batch', channels_data)


  def reset_password_navigation_link_click(self, **event_args):
    open_form('my_account.reset_password')
    pass





  

