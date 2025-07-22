from ._anvil_designer import helpTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil_extras.storage import local_storage

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

  def resync_button_click(self, **event_args):
    user = anvil.users.get_user()
    if user['smoobu_api_key'] is not None:
      result = alert(
        content="Hierdurch werden im Hintergrund alle Daten erneut synchronsiert. Dies ist normalerweise nicht notwendig, da neue Buchungen per API automatisiert empfangen werden. Die erneute Synchronisation dauert ca. 10 Minuten.",
        title="Re-synchronisation Starten?",
        buttons=[
          ("Ja", "YES"),
          ("Nein", "NO"),
        ]
      )
      if result == "YES":
        local_storage.clear()
        anvil.server.call('delete_bookings_by_email',anvil.users.get_user()['email'])
        
        open_form('dashboard')
        
        anvil.server.call_s('launch_sync_smoobu')
        pass
      else:
        # Code ausführen, wenn Benutzer Nein wählt oder das Popup schließt
        pass    
