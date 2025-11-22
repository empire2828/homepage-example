import anvil.server
from routing import router
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

user_has_subscription = False
user_email = None
request_count = 0
current_user = None

def say_hello():
  print("Hello, world")
