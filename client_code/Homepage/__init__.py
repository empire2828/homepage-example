from ._anvil_designer import HomepageTemplate
from anvil import *

class Homepage(HomepageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def about_us_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('AboutUs')

  def contact_us_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('ContactUs')

  def reset_links(self, **event_args):
    self.contact_us_link.role = ''
    self.about_us_link.role = ''
