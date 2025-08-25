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
    alert("Background sync started- this will take around 2 minutes.")
    anvil.server.call('launch_sync_smoobu')
    self.progress_bar.value = 0
    self.progress_bar.visible = True
    self.timer_1.interval = 0.5
    self.timer_1.enabled = True
    self.timer_1.visible = True
    alert("You will be forwarded to the settings.")
    open_form('my_account')
    pass

  def Data_protection_link_click(self, **event_args):
    open_form('data_protection')
    pass

  def timer_1_tick(self, **event_args):
    if not self.task:
      return
    try:
      state = self.task.get_state() or {}     # {'progress': int, 'total': int, 'message': str}
      progress = state.get('progress', 0)
      total = max(1, state.get('total', 100)) # Schutz gegen Division durch 0
      pct = int(round(progress * 100.0 / total))
      self.progress_bar.value = pct

      # Optional: Nachricht anzeigen, z. B. in einem Label
      # self.status_label.text = state.get('message', '')

      if self.task.is_completed():
        self.timer_1.enabled = False
        self.sync_smoobu_button.enabled = True
        self.sync_smoobu_button.text = "Sync abgeschlossen"
        self.progress_bar.value = 100
        # Weiterleitung oder UI-Update erst nach Abschluss:
        # open_form('my_account')
    except Exception:
      # Fehlerfall: Task-Fehler auswerten
      try:
        self.task.get_error()  # re-throw Server-Fehler, falls vorhanden
      except Exception as task_err:
        alert(f"Task-Fehler: {task_err}")
      finally:
        self.timer_1.enabled = False
        self.sync_smoobu_button.enabled = True
        self.sync_smoobu_button.text = "Sync starten"
        self.progress_bar.visible = False