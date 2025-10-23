from ._anvil_designer import helpTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil_extras.storage import local_storage

class help(helpTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

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
        open_form('dashboard')
        anvil.server.call_s('launch_sync_smoobu')
        pass
      else:
        # Code ausführen, wenn Benutzer Nein wählt oder das Popup schließt
        pass    

  def link_1_click(self, **event_args):
    """This method is called clicked"""
    pass
