from ._anvil_designer import helpTemplate
from anvil import *
import anvil.facebook.auth
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class help(helpTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.help_text_area.height=128
    # Any code you write here will run before the form opens.

  def help_send_button_click(self, **event_args):
    text=self.help_text_area.text
    file=self.help_file_loader.file
    user = anvil.users.get_user()
    if user is not None:
      email = user['email']
    anvil.server.call('send_email_to_support',text, file, email)
    alert('eMail wurde gesendet.')
    pass
