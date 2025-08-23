from ._anvil_designer import layout_templateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Cache only the iframe-heavy views
    self._views = {}
    # Show a default iframe view (optional)
    self.show_view("dashboard")

  # Public API to switch iframe views inside the container
  def show_view(self, name: str):
    # Lazily create the view if needed
    if name not in self._views:
      self._views[name] = self._create_view(name)
      # Replace 'content_panel' with your actual container component name
      self.content_panel.add_component(self._views[name])

    # Toggle visibility without removing components (prevents iframe reloads)
    for key, view in self._views.items():
      view.visible = (key == name)
      if view.visible and hasattr(view, "on_first_show"):
        try:
          view.on_first_show()
        except Exception as e:
          print(f"on_first_show error for {key}: {e}")

  # Factory for iframe-heavy views - imports inside methods work best in Anvil
  def _create_view(self, name: str):
    if name == "dashboard":
      from dashboard import dashboard
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
    raise ValueError(f"Unknown managed iframe view: {name}")

  def reset_links(self, **event_args):
    self.dashboard_navigation_link.selected = False
    self.profitability_navigation_link.selected = False
    self.bookings_navigation_link.selected = False
    self.cancellations_navigation_link.selected = False
    self.occupancy_navigation_link.selected = False
    self.lead_time_navigation_link.selected = False
    self.guest_insights_navigation_link.selected = False
    self.detailed_bookings_navigation_link.selected = False
    self.long_trends_navigation_link.selected = False
    self.connect_navigation_link.selected = False
    self.my_account_navigation_link.selected = False

  # Iframe views: use show_view to keep them mounted
  def dashboard_navigation_link_click(self, **event_args):
    self.reset_links()
    self.dashboard_navigation_link.selected = True
    self.show_view("dashboard")

  def profitability_navigation_link_click(self, **event_args):
    self.reset_links()
    self.profitability_navigation_link.selected = True
    self.show_view("profitability")

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.bookings_navigation_link.selected = True
    self.show_view("bookings")

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    self.cancellations_navigation_link.selected = True
    self.show_view("cancellations")

  def occupancy_navigation_link_click(self, **event_args):
    self.reset_links()
    self.occupancy_navigation_link.selected = True
    self.show_view("occupancy")

  def lead_time_navigation_link_click(self, **event_args):
    self.reset_links()
    self.lead_time_navigation_link.selected = True
    self.show_view("lead_time")

  def guest_insights_navigation_link_click(self, **event_args):
    self.reset_links()
    self.guest_insights_navigation_link.selected = True
    self.show_view("guest_insights")

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.detailed_bookings_navigation_link.selected = True
    self.show_view("detailed_bookings")

  def long_trends_navigation_link_click(self, **event_args):
    self.reset_links()
    self.long_trends_navigation_link.selected = True
    self.show_view("long_trends")

  # Non-iframe views: keep existing behavior (do not route through show_view)
  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    open_form('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    open_form('my_account')

  # Optional lifecycle
  def form_show(self, **event_args):
    pass



  

  
 
