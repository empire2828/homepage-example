from ._anvil_designer import faq_templateTemplate
from anvil import *

class faq_template(faq_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.faq_question_body.text = self.item['question']
    self.faq_answer_body.text = self.item['answer']
    self.faq_answer_body.visible = False

  def faq_answer_button_click(self, **event_args):
    self.faq_answer_body.visible= not self.faq_answer_body.visible
    pass
