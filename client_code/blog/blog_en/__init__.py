from ._anvil_designer import blog_enTemplate
from anvil import *
from routing import router
#import m3.components as m3
import anvil.server
import anvil.users

class blog_en(blog_enTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def cancellations_link_click(self, **event_args):
    open_form('blog.cancellations_en')
    pass

  def stly_link_click(self, **event_args):
    open_form('blog.stly_en')
    pass

  def vrbo_link_click(self, **event_args):
    open_form('blog.vrbo_en')
    pass
