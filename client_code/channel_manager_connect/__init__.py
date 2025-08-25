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
    self.task = None
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
    self.task = None #init
    self._navigate_when_done = False  # init
    
    alert("Background sync started- this will take around 2 minutes.")
    self.task = anvil.server.call('launch_sync_smoobu')
    self.progress_bar.value = 10
    print(self.progress_bar.value)
    self.status_label.text = 'Starting syncronisation'
    self.progress_bar.visible = True
    self.status_label.visible
    self.timer_1.interval = 1
    self.timer_1.enabled = True
    self.timer_1.visible = True
   
    self._navigate_when_done = True
    pass

  def Data_protection_link_click(self, **event_args):
    open_form('data_protection')
    pass

  def timer_1_tick(self, **event_args):
    if not self.task:
      return
  
      # Poll without spinner to avoid UI interruption
    with anvil.server.no_loading_indicator:
      try:
        state = self.task.get_state() or {}            # {'progress': int, 'total': int, 'message': str}
        progress = state.get('progress', 0)
        print(progress)
        self.progress_bar.progress = progress
        # Optionally reflect messages:
        self.status_label.text = state.get('message', '')
  
        if self.task.is_completed():                   # raises if the task failed
          self.timer_1.enabled = False
          self.progress_bar.progress = 1
          if self._navigate_when_done:
            alert("You will now be forwarded to the settings.")
            open_form('my_account')                    # navigate only after completion
      except Exception:
        # Surface server-side errors and stop polling
        self.timer_1.enabled = False
        self.progress_bar.visible = False
        try:
          # Re-throw original server error if present
          self.task.get_error()
        except Exception as e:
          alert(f"Task-Fehler: {e}")