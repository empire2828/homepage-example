from ._anvil_designer import StripePricingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class StripePricing(StripePricingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    #Any code you write here will run before the form opens.
    # pricing_table = self.dom_nodes['stripe-pricing-table']

    # Passes the user's email to the Stripe checkout. This ensures records match in both Stripe and the app.
    # pricing_table.setAttribute("customer-email", anvil.users.get_user()["email"])

@anvil.server.callable
def create_stripe_subscription(price_id, apartment_count):
    user = anvil.users.get_user()
    stripe_customer = anvil.stripe.get_customer(user['stripe_id'])  # Get existing customer
  
    # Calculate quantity based on apartment_count
    subscription = anvil.stripe.Subscription.create(
        customer=stripe_customer['id'],
        items=[{
            'price': price_id,
            'quantity': apartment_count  # Pass apartment_count as quantity
        }],
        payment_behavior='default_incomplete',
        expand=['latest_invoice.payment_intent']
    )
    return subscription


