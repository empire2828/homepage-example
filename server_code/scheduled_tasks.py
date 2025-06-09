import anvil.server
import anvil.http
from anvil.tables import app_tables
import time
from datetime import datetime, timedelta, timezone

@anvil.server.background_task
def download_and_store_blocklist():
  # Download the blocklist file
  url = "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/refs/heads/main/disposable_email_blocklist.conf"
  response = anvil.http.request(url, method="GET")
  content = response.get_bytes().decode("utf-8")

  # Split content into lines and filter out empty/comment lines
  domains = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

  # Clear the table before inserting new data
  for row in app_tables.disposable_domains.search():
    row.delete()

  # Insert domains into the table
  for domain in domains:
    app_tables.disposable_domains.add_row(domain=domain)

@anvil.server.callable
def launch_blocklist_download():
  task = anvil.server.launch_background_task('download_and_store_blocklist')
  return task

@anvil.server.background_task
def delete_old_bookings():
  today = datetime.now().date()
  cutoff_date = today - timedelta(days=14)
  matching_rows = app_tables.bookings.search(departure=lambda d: d <= cutoff_date)
  deleted_count = 0
  for row in matching_rows:
    row.delete()
    deleted_count += 1
  print(f"Buchungen gelöscht, deren Abreisedatum 14 Tage oder mehr zurückliegt. Anzahl: {deleted_count}")
  return deleted_count

