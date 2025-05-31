# Benötigte Libraries
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media
import csv
from datetime import datetime

@anvil.server.callable
def import_bookings_csv(csv_file):
  imported_count = 0

  # 1. Hole die Spaltennamen und Typen aus der Tabelle
  column_info = {c['name']: c['type'] for c in app_tables.bookings.list_columns()}  # z.B. {'email': 'string', ...}

  with anvil.media.TempFile(csv_file) as file_name:
    with open(file_name, 'r', encoding='utf-8-sig') as f:
      reader = csv.DictReader(f, quoting=csv.QUOTE_MINIMAL)
      for row in reader:
        processed_row = {}
        for col_name, value in row.items():
          clean_col_name = col_name.strip('"').strip()
          # Nur Spalten importieren, die es in der Tabelle gibt (und nicht ID)
          if clean_col_name == "ID" or clean_col_name not in column_info:
            continue
          if not value or not str(value).strip():
            continue  # Leere Werte überspringen
          clean_value = str(value).strip('"').strip()
          col_type = column_info[clean_col_name]
          try:
            # Typkonvertierung je nach Spaltentyp
            if col_type == 'date':
              for date_format in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                try:
                  processed_row[clean_col_name] = datetime.strptime(clean_value, date_format).date()
                  break
                except ValueError:
                  continue
              else:
                continue  # Kein gültiges Datumsformat, Spalte überspringen
            elif col_type == 'datetime':
              for datetime_format in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S', '%Y-%m-%d']:
                try:
                  if len(clean_value) == 10:
                    processed_row[clean_col_name] = datetime.strptime(clean_value, '%Y-%m-%d')
                  else:
                    processed_row[clean_col_name] = datetime.strptime(clean_value, datetime_format)
                  break
                except ValueError:
                  continue
              else:
                continue  # Kein gültiges Datetime-Format, Spalte überspringen
            elif col_type == 'number':
              clean_value = clean_value.replace(',', '.')
              try:
                processed_row[clean_col_name] = float(clean_value) if '.' in clean_value else int(clean_value)
              except Exception:
                continue  # Fehlerhafte Zahl, Spalte überspringen
            elif col_type == 'bool':
              processed_row[clean_col_name] = clean_value.lower() in ['true', '1', 'yes', 'ja', 'wahr']
            else:
              processed_row[clean_col_name] = clean_value
          except Exception:
            continue  # Fehlerhafte Spalte überspringen
        if processed_row:
          app_tables.bookings.add_row(**processed_row)
          imported_count += 1

  return f"{imported_count} Zeilen erfolgreich importiert"

