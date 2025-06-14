from ._anvil_designer import dashboardTemplate
from anvil import *
from anvil.tables import app_tables
from anvil import users
import anvil.server
from anvil_extras.storage import local_storage
import time
from datetime import datetime, timedelta

class dashboard(dashboardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    user = users.get_user()
    print('User Logged in: ',user['email'])

    dashboard_data = local_storage.get('dashboard_data')

    cache_too_old = False
    if dashboard_data:      
      last_login =  user['last_login'].replace(tzinfo=None)
      now = datetime.now()
      if now - last_login > timedelta(days=3):
        cache_too_old = True
        print('Cache too old', last_login,now)
    else:
      cache_too_old = True

    local_storage_update_needed = True
    if user is not None and dashboard_data is not None:
      if ('server_data_last_update' in dashboard_data and
          user['server_data_last_update'] is not None and 
          dashboard_data['server_data_last_update'] is not None):
        if dashboard_data['server_data_last_update'] >= user['server_data_last_update']:
          local_storage_update_needed = False

    if dashboard_data is not None:
      local_date = dashboard_data.get('server_data_last_update')
      if local_date is not None:
        print('local_date', local_date)

    if user is not None:
      server_date = user.get('server_data_last_update')
      if server_date is not None:
        print('server_date', server_date)

    print('dashboard data not None: ', dashboard_data is not None, 'local_storage_update_needed: ',local_storage_update_needed,'cache too old: ',cache_too_old)

    if not dashboard_data or cache_too_old or local_storage_update_needed:
      dashboard_data = anvil.server.call('get_dashboard_data_dict')
      local_storage['dashboard_data'] = dashboard_data

    user_has_subscription= dashboard_data['has_subscription']

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
      panel_data = dashboard_data['bookings']
    else: 
      panel_data = dashboard_data.get('bookings', [])  # Initialize with empty list as fallback
    bookings = panel_data
    apartments = set()
    self.panel_data = panel_data     # Speichere panel_data als Instanzvariable

    for booking in bookings:
      apartment_name = booking.get('apartment', '')  # Direkt als String behandeln
      if apartment_name:  # Nur hinzufügen wenn nicht leer
        apartments.add(apartment_name)

    dropdown_items = sorted(list(apartments))
    self.apartment_dropdown_menu.items = dropdown_items
    self.apartment_dropdown_menu.include_placeholder = True
    self.apartment_dropdown_menu.placeholder = "Apartment wählen"

    # Setze das erste Apartment als Standard-Auswahl
    if dropdown_items:  # Prüfe ob Items vorhanden sind
      self.apartment_dropdown_menu.selected_value = dropdown_items[0]

      # Filtere auch sofort die Bookings für das erste Apartment
      first_apartment = dropdown_items[0]
      filtered_bookings = [
        booking for booking in self.panel_data  # Verwende self.panel_data
        if booking.get('apartment') == first_apartment
      ]
      self.panel_data_selected = filtered_bookings
    else:
      self.apartment_dropdown_menu.selected_value = None
      self.panel_data_selected = self.panel_data

    #self.build_revenue_graph()
    self.bookings_repeating_panel.items= self.panel_data_selected
    #print(self.panel_data_selected)
    #self.pivot_1.items = self.panel_data_selected
    self.pivot_2.rows = ["guest_count"]
    self.pivot_2.columns = ["children"]
    self.pivot_2.values = ["revenue"]
    self.pivot_2.aggregator = "sum"
    
    # Then assign the data
    self.pivot_2.items = [
      {"guest_count": 2, "children": 0, "revenue": 120},
      {"guest_count": 2, "children": 1, "revenue": 150},
      {"guest_count": 3, "children": 2, "revenue": 200},
      {"guest_count": 2, "children": 0, "revenue": 80},
      {"guest_count": 3, "children": 1, "revenue": 170},
      {"guest_count": 2, "children": 1, "revenue": 130},
      {"guest_count": 3, "children": 2, "revenue": 220},
      {"guest_count": 4, "children": 0, "revenue": 300},
      {"guest_count": 4, "children": 1, "revenue": 350},
    ]

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









