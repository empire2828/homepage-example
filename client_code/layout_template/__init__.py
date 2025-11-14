from ._anvil_designer import layout_templateTemplate
from anvil import *
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

  def profitability_navigation_link_click(self, **event_args):
    self.reset_links()
    self.profitability_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(2)  # Profitability

  def bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.bookings_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(3)  # Long Trends

  def cancellations_navigation_link_click(self, **event_args):
    self.reset_links()
    self.cancellations_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(4)  # Cancellations

  def occupancy_navigation_link_click(self, **event_args):
    self.reset_links()
    self.occupancy_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(5)  # Occupancy

  def lead_time_navigation_link_click(self, **event_args):
    self.reset_links()
    self.lead_time_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(6)  # Lead Time

  def guest_insights_navigation_link_click(self, **event_args):
    self.reset_links()
    self.guest_insights_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(7)  # Guest Insights

  def long_trends_navigation_link_click(self, **event_args):
    self.reset_links()
    self.long_trends_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(8)  # Long Trends

  def detailed_bookings_navigation_link_click(self, **event_args):
    self.reset_links()
    self.detailed_bookings_navigation_link.selected = True
    multiframe_form = self.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(9)  # Detailed Bookings

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



