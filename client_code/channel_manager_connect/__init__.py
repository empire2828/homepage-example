from ._anvil_designer import channel_manager_connectTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class channel_manager_connect(channel_manager_connectTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
   # Any code you write here will run before the form opens.
 
  def save_api_key_button_click(self, **event_args):
    api_key = self.api_key_text_box.text       
        # Serveraufruf zum Speichern des API-Keys
    try:
      erfolg = anvil.server.call('save_user_api_key', api_key)
      if erfolg:
        anvil.Notification("API-Key erfolgreich gespeichert").show()
    except Exception as e:
      anvil.alert(f"Fehler beim Speichern des API-Keys: {str(e)}")
    pass

  def sync_smoobu_button_click(self, **event_args):
    alert("Hintergrund- Synchronisation wird gestartet. Das dauert ca. 5 Minuten.")
    anvil.server.call('launch_sync_smoobu')
    user = anvil.users.get_user()
    user_email = user['email']
    anvil.server.call('save_last_fees_as_std',user_email)
    pass

  def Data_protection_link_click(self, **event_args):
    open_form('data_protection')
    pass