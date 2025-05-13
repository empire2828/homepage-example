import anvil.facebook.auth
#import anvil.email
import anvil.http
import urllib.parse
import anvil.secrets

# Google Custom Search Engine ID
cse_id = "f4731bf6df41348f2"

# Google API Key
api_key = anvil.secrets.get_secret('google_linkedin_search')

# URL der API
url = "https://www.googleapis.com/customsearch/v1"

@anvil.server.callable
def google_linkedin(full_name, city):
    if full_name is None:
        full_name = ""
    if city is None:
        city = ""
  
    # Ersetze Leerzeichen im Namen durch Pluszeichen, um sicherzustellen, dass alle Wörter gesucht werden
    query_name = full_name.replace(" ", "+")
    
    # Einrichten der Abfrageparameter
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": f"site:linkedin.com \"{query_name}\" {city}",  # Vollständiger Name in Anführungszeichen und Stadt separat
        "num": 1  # Nur ein Ergebnis zurückgeben
    }
    
    try:
        # Kodieren der Abfrageparameter und Anhängen an die URL
        encoded_params = urllib.parse.urlencode(params)
        full_url = f"{url}?{encoded_params}"
        
        # HTTP-Anfrage mithilfe der Anvil-Bibliothek mit json=True
        response = anvil.http.request(full_url, method="GET", json=True)
        
        # Extrahieren und Rückgabe des Titels des ersten Suchergebnisses, wenn der vollständige Name vorhanden ist
        if "items" in response and len(response["items"]) > 0:
            first_result = response["items"][0]
            title = first_result.get("title", "")
            snippet = first_result.get("snippet", "")
            if full_name.lower() in title.lower() or full_name.lower() in snippet.lower():
                return title
            else:
                return None
        else:
            return None
    
    except Exception as e:
        print(f"Fehler beim Suchen nach LinkedIn-Profilen: {e}")
        return None

# Beispielanwendung
# full_name = "Dirk Klemer"
# city = "Hamburg"
# title = google_linkedin(full_name, city)
# if title:
#  print(title)