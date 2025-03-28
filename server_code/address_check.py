import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.http
import json
import urllib.parse

api_key = anvil.secrets.get_secret('google_maps_api_key')

@anvil.server.callable
def address_check(address):
    encoded_address = urllib.parse.quote(address)  # Vollständige Kodierung
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    
    try:
        response = anvil.http.request(url, json=True)
        
        if 'status' in response and response['status'] == 'OK':
            if 'results' in response and len(response['results']) > 0:
                # address check passed
                print("Address check passed: ", response['results'][0]['formatted_address'])
                return True
            else:
                # keine Ergebnisse gefunden
                print("No results found!")
                return False
        elif response['status'] == 'ZERO_RESULTS':
            print("Address not found in Google's database.")
            return False
        else:
            print("API call error:", response['status'])
            return False
    except anvil.http.HttpError as e:
        print(f"API call error: {e.status}")
        return False

# Beispielaufruf
# address = "Sodenkamp 4e, 22337 Hamburg"
# result = address_check(address)