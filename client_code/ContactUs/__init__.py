from ._anvil_designer import ContactUsTemplate
from anvil import *

class ContactUs(ContactUsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    self.layout.reset_links()
    self.layout.contact_us_link.role = 'selected'

