from ._anvil_designer import faq_templateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class faq_template(faq_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def faq_answer_button_click(self, **event_args):
    self.faq_answer_body.visible= not self.faq_answer_body.visible
    pass
