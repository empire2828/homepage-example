from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
import time
from datetime import datetime, timedelta
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    user = users.get_user()
    print('User Logged in: ',user['email'])

    user_has_subscription= anvil.server.call('get_user_has_subscription')

    if user['smoobu_api_key'] is None:
      self.pms_need_to_connect_text.visible = True
      #self.refresh_button.visible = False
      self.apartment_dropdown_menu.visible = False
      self.resync_smoobu_button.visible = False
      self.chanel_manager_connect_button.visible = True
    else:
      if user_has_subscription is False:
        self.dashboard_upgrade_needed_text.visible = True
        self.dashboard_upgrade_button.visible = True
        self.pms_need_to_connect_text.visible = False
        self.apartment_dropdown_menu.visible = False
        self.chanel_manager_connect_button.visible = False
        self.bookings_repeating_panel.visible = False

    if user_has_subscription:
      email= user['email']
      self.init_iframe(email)
    else: 
      pass
    
  def init_iframe(self, supabase_key):
    base_url = "https://lookerstudio.google.com/embed/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de/page/qmCOF"
    #https://lookerstudio.google.com/reporting/d1557a62-b6f7-470e-93b1-42e5c54ef3de
    params = {"supabase_key": supabase_key}

    # URL mit Parameter kodieren
    encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
    iframe_url = f"{base_url}{encoded_params}"
    print (iframe_url)

    # iFrame erstellen und einbinden
    iframe = jQuery("<iframe>").attr({
      "src": iframe_url,
      "width": "100%",
      "height": "800px",
      "frameborder": "0"
    })
    iframe.appendTo(get_dom_node(self.flow_panel))

  
  ######################################
 
  def apartment_dropdown_menu_change(self, **event_args):
    selected_apartment_name = self.apartment_dropdown_menu.selected_value
    if selected_apartment_name is not None:
      filtered_bookings = [
        booking for booking in self.panel_data  # Verwende self.panel_data
        if booking.get('apartment') == selected_apartment_name
      ]
      self.bookings_repeating_panel.items = filtered_bookings
    else:
      self.bookings_repeating_panel.items = self.panel_data  # Verwende self.panel_data


  def form_refreshing_data_bindings(self, **event_args):
    """This method is called when refresh_data_bindings is called"""
    pass

  def sync_smoobu_button_click(self, **event_args):
    anvil.server.call_s('launch_sync_smoobu')
    anvil.server.call_s('launch_get_bookings_risk')
    alert("Sync in process.")
    pass

  def refresh_button_click(self, **event_args):
    local_storage.clear()
    self.bookings_repeating_panel.items = []
    self.form_show()
    self.refresh_data_bindings()
    pass

  def chanel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')
    pass

  def dashboard_upgrade_button_click(self, **event_args):    
    try:
      user = anvil.users.get_user()
      if not user:
        alert('Kein Benutzer angemeldet')
        return

      subscription = user.get('subscription')
      apartment_count = user.get('apartment_count', 0) or 1

      if subscription != 'Subscription' and apartment_count < 4:
        open_form('StripePricing')
      elif subscription != 'Pro-Subscription' and apartment_count > 3:
        open_form('StripePricing_pro')
      else:
        alert('Abo bereits vorhanden.')
    except Exception as e:
      alert(f'Ein Fehler ist aufgetreten: {e}')
  pass
  #identisch zu pflegen in Layout!

  def build_revenue_graph(self):
    # Gesamtsumme berechnen
    total_revenue = sum(booking.get('price', 0) for booking in self.panel_data_selected)
    print(total_revenue)
    self.revenue_display.text = f"Gesamtumsatz: {total_revenue:.2f} €"
  
    # Umsatz nach Monat plotten
    from collections import defaultdict
    revenue_by_month = defaultdict(float)
    for booking in self.panel_data_selected:
      date = booking.get('arrival')
      price = booking.get('price', 0)
      if date:
        month = date[:7]
        revenue_by_month[month] += price
  
    months = sorted(revenue_by_month.keys())
    revenues = [revenue_by_month[m] for m in months]
  
    import plotly.graph_objects as go
    self.revenue_plot.data = go.Bar(
      x=months,
      y=revenues,
      marker=dict(color='#2196f3')
    )









