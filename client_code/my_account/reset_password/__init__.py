from ._anvil_designer import reset_passwordTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class reset_password(reset_passwordTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Corrected code inside __init__ method:
    if confirm("Resetting your password will send a reset email to your inbox and log you out. Do you want to continue?"):
      current_user = anvil.users.get_user()  # Get logged-in user
      if current_user:
        anvil.users.send_password_reset_email(current_user['email'])  # Use current_user[1][2]
        alert("A password reset email has been sent to your inbox.", title="Password reset email sent")
        anvil.users.logout()
        open_form("homepage")
      else:
        alert("No user is logged in.", title="Error")

