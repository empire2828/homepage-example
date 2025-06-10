from ._anvil_designer import pivotTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from plotly import graph_objects as go

class pivot(pivotTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
  
    # Get your data from the server
    pivot_data = anvil.server.call('get_dashboard_data_dict')
    bookings = pivot_data['bookings']
  
    # Extract data for plotting
    channel_names = [booking['channel_name'] for booking in bookings if booking['channel_name']]
    adults_count = [booking['adults'] for booking in bookings if booking['adults']]
  
    # Create a bar chart
    self.plot_1.data = go.Bar(x=channel_names, y=adults_count)
  
    # Optional: Configure layout
    self.plot_1.layout = {
      'title': 'Adults by Channel',
      'xaxis': {'title': 'Channel'},
      'yaxis': {'title': 'Number of Adults'}
    }
