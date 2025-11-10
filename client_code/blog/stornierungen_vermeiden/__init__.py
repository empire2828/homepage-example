from ._anvil_designer import stornierungen_vermeidenTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from plotly import graph_objects as go

class stornierungen_vermeiden(stornierungen_vermeidenTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    channels = ["Booking.com", "Airbnb", "Vrbo/Fewo-Direkt", "Direkt"]
    cancel_pct = [42, 25, 25, 10]  # Beispielwerte in %
    
    # Definiere die Farben je Kanal (Farbcodes im Plotly-Format: Strings)
    channel_colors = [
      "#0071CE",  # Booking.com Blau
      "#FF5A5F",  # Airbnb Rot
      "#FF9900",  # Vrbo/Fewo-Direkt Orange
      "#2ECC40"   # Direkt Grün
    ]
    
    fig = go.Figure(
      data=[
        go.Bar(
          x=channels,
          y=cancel_pct,
          text=[f"{p:.1f}%" for p in cancel_pct],
          textposition="auto",
          marker_color=channel_colors
        )
      ]
    )
    fig.update_layout(
      title="Stornierungsraten nach Kanal",
      xaxis_title="Buchungskanal",
      yaxis=dict(visible=False),
      margin=dict(l=10, r=10, t=50, b=40)
    )
    
    self.plot_channel_cancellations.figure = fig
