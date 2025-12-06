from ._anvil_designer import blog_deTemplate
from anvil import *
from routing import router
#import m3.components as m3
import anvil.server
import anvil.users

class blog_de(blog_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def cancellations_link_click(self, **event_args):
    open_form('blog.cancellations_de')
    pass

  def stly_link_click(self, **event_args):
    open_form('blog.stly_de')
    pass

  def vrbo_link_click(self, **event_args):
    open_form('blog.vrbo_de')
    pass

  def ota_markuplink_click(self, **event_args):
    open_form('blog.ota_markup_de')
    pass

