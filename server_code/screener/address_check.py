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
    # Prüfen, ob die Adresse leer ist
    if not address:
        print("Leere Adresse übergeben")
        return False
    
    try:
        encoded_address = urllib.parse.quote(address)  # Vollständige Kodierung
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        
        try:
            response = anvil.http.request(url, json=True)
            
            if response and 'status' in response:
                if response['status'] == 'OK' and 'results' in response and len(response['results']) > 0:
                    # Address check passed
                    print("Address check passed: ", response['results'][0]['formatted_address'])
                    return True
                else:
                    # Keine Ergebnisse oder anderer Status
                    print(f"Address check failed: {response.get('status', 'Unknown error')}")
                    return False
            else:
                # Ungültige Antwort
                print("Invalid API response")
                return False
        except anvil.http.HttpError as e:
            print(f"API call error: {e.status}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False
    except Exception as e:
        print(f"Error encoding address: {str(e)}")
        return False

# Beispielaufruf
# address = "Sodenkamp 4e, 22337 Hamburg"
# result = address_check(address)
