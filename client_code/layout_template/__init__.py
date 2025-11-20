from ._anvil_designer import layout_templateTemplate
from anvil import *
from routing import router
import m3.components as m3
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..LookerStudio.multiframe import multiframe

class layout_template(layout_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)    
    # Keine multiframe Initialisierung hier!
    self.current_multiframe = None
    user = anvil.users.get_user()    
    if user is not None:
      email = user['email']
      user_has_subscription = anvil.server.call_s('get_user_has_subscription_for_email')
      if user_has_subscription is False:
        self.my_account_navigation_link.badge = True
        request_count = anvil.server.call_s('get_request_count')
        self.my_account_navigation_link.badge_count = request_count

  def open_multiframe_form(self):
    #"""Öffnet die multiframe Form als Hauptinhalt"""

    # Schließe vorherige multiframe falls vorhanden
    if self.current_multiframe:
      self.current_multiframe.remove_from_parent()

    # Erstelle neue multiframe Instanz
    self.current_multiframe = multiframe()

    # Öffne als neue Form
    open_form(self.current_multiframe)
    #print("✅ multiframe Form geöffnet")

    return self.current_multiframe

  def reset_links(self, **event_args):
    self.dashboard_navigation_link.selected = False
    self.monthly_outlook_navigation_link.selected = False
    self.profitability_navigation_link.selected = False
    self.bookings_navigation_link.selected = False
    self.cancellations_navigation_link.selected = False
    self.occupancy_navigation_link.selected = False
    self.lead_time_navigation_link.selected = False
    self.guest_insights_navigation_link.selected = False
    self.detailed_bookings_navigation_link.selected = False
    self.long_trends_navigation_link.selected = False
    self.connect_navigation_link.selected = False
    self.knowledge_hub_link.selected = False
    self.my_account_navigation_link.selected = False
    self.layout.hide_nav_drawer()

  def dashboard_navigation_link_click(self, **event_args):
    self.reset_links()
    #self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')
    if self.my_account_navigation_link.badge is False:
      is_user_below_request_count = anvil.server.call_s('is_user_below_request_count')
      if is_user_below_request_count is False:
        open_form('upgrade')
    self.dashboard_navigation_link.selected = True
    self.layout.hide_nav_drawer()
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(0)  # Dashboard

  def monthly_outlook_navigation_link_click(self, **event_args):
    self.reset_links()
    self.monthly_outlook_navigation_link.selected = True
    self.layout.hide_nav_drawer()
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(1)  # Dashboard
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def profitability_navigation_link_click(self, **event_args):
    self.reset_links()
    self.profitability_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(2)  # Profitability
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.bookings_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(3)  # Long Trends
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    self.cancellations_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(4)  # Cancellations
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def occupancy_navigation_link_click(self, **event_args):
    self.reset_links()
    self.occupancy_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(5)  # Occupancy
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def lead_time_navigation_link_click(self, **event_args):
    self.reset_links()
    self.lead_time_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(6)  # Lead Time
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def guest_insights_navigation_link_click(self, **event_args):
    self.reset_links()
    self.guest_insights_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(7)  # Guest Insights
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def long_trends_navigation_link_click(self, **event_args):
    self.reset_links()
    self.long_trends_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(8)  # Long Trends
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.detailed_bookings_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(9)  # Detailed Bookings
    self.my_account_navigation_link.badge_count = anvil.server.call_s('add_request_count')

  def connect_navigation_link_click(self, **event_args):
    self.reset_links()
    self.connect_navigation_link.selected = True
    open_form('channel_manager_connect')
    pass

  def upgrade_navigation_link_click(self, **event_args):
    self.reset_links()
    pass

  def my_account_navigation_link_click(self, **event_args):
    self.reset_links()
    self.my_account_navigation_link.selected = True
    open_form('my_account')
    pass

  def knowledge_hub_link_click(self, **event_args):
    self.reset_links()
    self.knowledge_hub_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(10)  # Knowledge Hub



