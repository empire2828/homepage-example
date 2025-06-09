import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def is_not_disposable_email(email):
  """
    Checks if the given email address belongs to a domain in the disposable_domains table.
    Returns True if the domain is found, otherwise False.
    """
  # Extract the domain part of the email
  try:
    domain = email.split('@')[1].strip().lower()
  except (IndexError, AttributeError):
    return False  # Invalid email format

    # Check if the domain exists in the table
  return app_tables.disposable_domains.get(domain=domain) is None