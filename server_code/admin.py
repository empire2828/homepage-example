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
from io import StringIO

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
def import_bookings_csv(csv_file):
  imported_count = 0

  try:
    # Methode 1: Mit TempFile (empfohlen)
    with anvil.media.TempFile(csv_file) as file_name:
      with open(file_name, 'r', encoding='utf-8-sig') as f:
        # CSV mit verschiedenen Optionen lesen
        reader = csv.DictReader(f, quoting=csv.QUOTE_MINIMAL)

        for row in reader:
          processed_row = {}

          for col_name, value in row.items():
            # Anführungszeichen und Leerzeichen von Spaltennamen entfernen
            clean_col_name = col_name.strip('"').strip()

            # Leere Werte als None behandeln
            if not value or not str(value).strip():
              processed_row[clean_col_name] = None
              continue

              # Anführungszeichen von Werten entfernen
            clean_value = str(value).strip('"').strip()

            # Typkonvertierung basierend auf Spaltendefinition
            col_type = COLUMN_TYPES.get(clean_col_name, 'string')

            try:
              if col_type == 'date':
                # Verschiedene Datumsformate versuchen
                for date_format in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                  try:
                    processed_row[clean_col_name] = datetime.strptime(clean_value, date_format).date()
                    break
                  except ValueError:
                    continue
                else:
                  raise ValueError(f"Ungültiges Datumsformat: {clean_value}")

              elif col_type == 'datetime':
                # Verschiedene Datetime-Formate versuchen
                for datetime_format in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S', '%Y-%m-%d']:
                  try:
                    if len(clean_value) == 10:  # Nur Datum
                      processed_row[clean_col_name] = datetime.strptime(clean_value, '%Y-%m-%d')
                    else:
                      processed_row[clean_col_name] = datetime.strptime(clean_value, datetime_format)
                    break
                  except ValueError:
                    continue
                else:
                  raise ValueError(f"Ungültiges Datetime-Format: {clean_value}")

              elif col_type == 'number':
                # Kommas durch Punkte ersetzen für deutsche Zahlenformate
                clean_value = clean_value.replace(',', '.')
                processed_row[clean_col_name] = float(clean_value) if '.' in clean_value else int(clean_value)

              elif col_type == 'bool':
                processed_row[clean_col_name] = clean_value.lower() in ['true', '1', 'yes', 'ja', 'wahr']

              else:
                processed_row[clean_col_name] = clean_value

            except Exception as e:
              raise ValueError(f"Fehler in Zeile {reader.line_num}, Spalte {clean_col_name}: {str(e)}")

              # Zeile in die Tabelle einfügen
          app_tables.bookings.add_row(**processed_row)
          imported_count += 1

  except Exception as e:
    # Fallback: Mit get_bytes() versuchen
    try:
      csv_bytes = csv_file.get_bytes()
      csv_str = csv_bytes.decode('utf-8-sig')
      reader = csv.DictReader(StringIO(csv_str))

      for row in reader:
        processed_row = {}

        for col_name, value in row.items():
          clean_col_name = col_name.strip('"').strip()

          if not value or not str(value).strip():
            processed_row[clean_col_name] = None
            continue

          clean_value = str(value).strip('"').strip()
          col_type = COLUMN_TYPES.get(clean_col_name, 'string')

          try:
            if col_type == 'date':
              for date_format in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                try:
                  processed_row[clean_col_name] = datetime.strptime(clean_value, date_format).date()
                  break
                except ValueError:
                  continue
            elif col_type == 'datetime':
              for datetime_format in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S', '%Y-%m-%d']:
                try:
                  processed_row[clean_col_name] = datetime.strptime(clean_value, datetime_format)
                  break
                except ValueError:
                  continue
            elif col_type == 'number':
              clean_value = clean_value.replace(',', '.')
              processed_row[clean_col_name] = float(clean_value) if '.' in clean_value else int(clean_value)
            elif col_type == 'bool':
              processed_row[clean_col_name] = clean_value.lower() in ['true', '1', 'yes', 'ja', 'wahr']
            else:
              processed_row[clean_col_name] = clean_value
          except Exception as e:
            raise ValueError(f"Fehler in Zeile {reader.line_num}, Spalte {clean_col_name}: {str(e)}")

        app_tables.bookings.add_row(**processed_row)
        imported_count += 1

    except Exception as fallback_error:
      raise Exception(f"Import fehlgeschlagen. Ursprünglicher Fehler: {str(e)}. Fallback-Fehler: {str(fallback_error)}")

  return f"{imported_count} Zeilen erfolgreich importiert"
