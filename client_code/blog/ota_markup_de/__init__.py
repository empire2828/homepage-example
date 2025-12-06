from ._anvil_designer import ota_markup_deTemplate
from anvil import *
import anvil.server
from routing import router
import m3.components as m3
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ota_markup_de(ota_markup_deTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def ota_commission_text_box_pressed_enter(self, **event_args):
    self.calculate_ota_markup()
    pass

  def calculate_ota_markup(self, **event_args):
    ota_comm = 0
    if self.ota_commission_text_box.text:
      ota_comm = int(self.ota_commission_text_box.text)
    if self.vat_checkbox:
      ota_markup_result = (100 / (100 - ota_comm) - 1) * 100
    ota_markup_result_rounded = round(ota_markup_result, 2)
    self.ota_markup_result_body.text = f"{ota_markup_result_rounded:.2f} %"
    return 
