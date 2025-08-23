from ._anvil_designer import mainTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class main(mainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def show_view(self, name):
    # Lazy instantiate
    if name not in self._views:
      self._views[name] = self._create_view(name)
      self.content_panel.add_component(self._views[name])

    # Show requested, hide others (do not clear/remove)
    for key, view in self._views.items():
      view.visible = (key == name)
      if view.visible and hasattr(view, "on_first_show"):
        view.on_first_show()  # optional hook to init iframe lazily

  def _create_view(self, name):
    if name == "dashboard":
      from .dashboard import dashboard
      return dashboard()
    if name == "profitability":
      from .reports import reports
      return reports()
    # ... other 6 forms
    raise ValueError(f"Unknown view: {name}")

