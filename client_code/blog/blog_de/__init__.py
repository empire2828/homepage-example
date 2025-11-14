from ._anvil_designer import blog_deTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class blog_de(blog_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def cancellations_link_click(self, **event_args):
    open_form('blog.cancellations_de')
    pass
