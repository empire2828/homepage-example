from ._anvil_designer import channel_manager_connectTemplate
from anvil import *
import m3.components as m3
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
    self.last_progress_from_task = 0
    self.last_progress_seen = 0
   # Any code you write here will run before the form opens.
 
  def save_api_key_button_click(self, **event_args):
    api_key = self.api_key_text_box.text   
    current_user = anvil.users.get_user()
        # Serveraufruf zum Speichern des API-Keys
    try:
      erfolg = anvil.server.call('save_user_api_key', api_key)
      if erfolg:
        anvil.Notification("API-Key sucessfully saved").show()
    except Exception as e:
      anvil.alert(f"Error on saving API-Key: {str(e)}")
      print(current_user['email'],f"Error on saving API-Key: {str(e)}")    
    result = anvil.server.call('validate_smoobu_api_key',current_user['email'])    
    if not result.get("valid"):
      anvil.alert('Smoobu said API Key is not correct. It should look like: jgfKvbu1Sdrqu5INRO0kwjV07fed1xrls22FJIFABY. If correct, just press save again as Smoobu is sometimes slow...',large=True)
      print(current_user['email']," API Key not correct", result)
      return
    pass

  def sync_smoobu_button_click(self, **event_args):
    self.task = None #init
    self._navigate_when_done = False  # init
    current_user = anvil.users.get_user()
    result = anvil.server.call('validate_smoobu_api_key',current_user['email'])    
    if not result.get("valid"):
      anvil.alert('API Key is not correct or not yet saved. It should look like this one: jgfKvbu1Sdrqu5INRO0kwjV07fed1xrls22FJIFABY',large=True)
      print(current_user['email']," API Key not correct", result)
      return
    alert("Background sync started- this will take around 2 minutes.")
    self.task = anvil.server.call('launch_sync_smoobu')
    self.progress_bar.value = 3
    self.progress_bar.visible = True
    self.timer_1.interval = 2
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
    # Robust: Fehlerbehandlung schützt UI
    with anvil.server.no_loading_indicator:
      try:
        state = self.task.get_state() or {}
        progress_from_task = state.get('progress', None)
        # Wenn neue Taskdaten kommen, diese übernehmen
        if progress_from_task is not None and progress_from_task > self.last_progress_from_task:
          self.last_progress_from_task = progress_from_task
          self.progress_bar.progress = progress_from_task
        else:
          # Kein neues Progress, inkrementiere sanft
          self.progress_bar.progress = min(self.progress_bar.progress + 0.005, 1.0)
        # Optional: Statuslabel wie gehabt
        self.status_label.text = state.get('message', '')
        if self.task.is_completed():
          self.timer_1.enabled = False
          self.progress_bar.progress = 1
          if self._navigate_when_done:
            alert("You will now be forwarded to the settings.")
            open_form('my_account')
      except Exception:
        self.timer_1.enabled = False
        self.progress_bar.visible = False
        try:
          self.task.get_error()
        except Exception as e:
          alert(f"Task-Fehler: {e}")
