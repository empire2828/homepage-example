from ._anvil_designer import StripePricing_proTemplate
from anvil import *
import anvil.facebook.auth
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class StripePricing_pro(StripePricing_proTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    pricing_table_pro = self.dom_nodes['stripe-pricing-table-pro']

    # Passes the user's email to the Stripe checkout. This ensures records match in both Stripe and the app.
    pricing_table_pro.setAttribute("customer-email", anvil.users.get_user()["email"])

