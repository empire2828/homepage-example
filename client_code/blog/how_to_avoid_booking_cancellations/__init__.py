from ._anvil_designer import how_to_avoid_booking_cancellationsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from plotly import graph_objects as go

class how_to_avoid_booking_cancellations(how_to_avoid_booking_cancellationsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    channels = ["Booking.com", "Airbnb", "Vrbo"]
    cancel_pct = [42, 12, 15.9]  # Beispielwerte in %
    
    fig = go.Figure(
      data=[go.Bar(
        x=channels,
        y=cancel_pct,
        text=[f"{p:.1f}%" for p in cancel_pct],
        textposition="auto"  # Werte sichtbar ohne y-Achse
      )]
    )
    fig.update_layout(
      title="Stornierungsraten nach Kanal",
      xaxis_title="Buchungskanal",
      # y-Achse ausblenden
      yaxis=dict(visible=False),
      # optional etwas weniger linker Rand, wenn gewünscht
      margin=dict(l=10, r=10, t=50, b=40)
    )
    
    self.plot_channel_cancellations.figure = fig
