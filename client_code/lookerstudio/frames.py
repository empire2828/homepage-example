import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

def get_form(name):
  """Factory function to create iframe forms by name"""

  if name == "dashboard":
    from .dashboard import dashboard
    return dashboard()

  if name == "profitability":
    from .profitability import profitability
    return profitability()

  if name == "bookings":
    from .bookings import bookings
    return bookings()

  if name == "cancellations":
    from .cancellations import cancellations
    return cancellations()

  if name == "occupancy":
    from .occupancy import occupancy
    return occupancy()

  if name == "lead_time":
    from .lead_time import lead_time
    return lead_time()

  if name == "guest_insights":
    from .guest_insights import guest_insights
    return guest_insights()

  if name == "detailed_bookings":
    from .detailed_bookings import detailed_bookings
    return detailed_bookings()

  if name == "long_trends":
    from .long_trends import long_trends
    return long_trends()

  raise ValueError(f"Unknown iframe form: {name}")
