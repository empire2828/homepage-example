import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import csv
from io import StringIO
from datetime import datetime

# Deine Tabellenstruktur (als Lookup für Datentypen)
COLUMN_TYPES = {
  'email': 'string',
  'apartment': 'string',
  'arrival': 'date',
  'departure': 'date',
  'channel_name': 'string',
  'guestname': 'string',
  'adults': 'number',
  'children': 'number',
  'language': 'string',
  'type': 'string',
  'created-at': 'datetime',
  'reservation_id': 'number',
  'guestid': 'number',
  'phone': 'string',
  'address_street': 'string',
  'address_postalcode': 'string',
  'address_city': 'string',
  'address_country': 'string',
  'screener_openai_job': 'string',
  'screener_address_check': 'bool',
  'screener_google_linkedin': 'string',
  'screener_openai_age': 'string',
  'screener_phone_check': 'bool'
}

@anvil.server.callable
def import_bookings_csv(csv_data):
  # CSV-Daten dekodieren
  csv_str = csv_data.decode('utf-8-sig')  # Handle BOM
  reader = csv.DictReader(StringIO(csv_str))

  for row in reader:
    processed_row = {}

    for col_name, value in row.items():
      # Leere Werte als None behandeln
      if not value.strip():
        processed_row[col_name] = None
        continue

        # Typkonvertierung basierend auf Spaltendefinition
      col_type = COLUMN_TYPES.get(col_name, 'string')

      try:
        if col_type == 'date':
          processed_row[col_name] = datetime.strptime(value, '%Y-%m-%d').date()
        elif col_type == 'datetime':
          processed_row[col_name] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        elif col_type == 'number':
          processed_row[col_name] = float(value) if '.' in value else int(value)
        elif col_type == 'bool':
          processed_row[col_name] = value.lower() in ['true', '1', 'yes']
        else:
          processed_row[col_name] = value.strip()
      except Exception as e:
        raise ValueError(f"Fehler in Zeile {reader.line_num}, Spalte {col_name}: {str(e)}")

        # Zeile in die Tabelle einfügen
    app_tables.bookings.add_row(**processed_row)

  return f"{reader.line_num - 1} Zeilen importiert"

