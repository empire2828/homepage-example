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
    self._views = {}
    self.show_view("dashboard")

  def show_view(self, name: str):
    if name not in self._views:
      self._views[name] = self._create_view(name)
      self.content_panel.add_component(self._views[name])

    for key, view in self._views.items():
      view.visible = (key == name)
      if view.visible and hasattr(view, "on_first_show"):
        view.on_first_show()

  def _create_view(self, name: str):
    # Import the factory function from lookerstudio module
    from ..lookerstudio.frames import get_form
    return get_form(name)

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

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    open_form('channel_manager_connect')

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    open_form('my_account')

  def form_show(self, **event_args):
    pass


  

  
 
