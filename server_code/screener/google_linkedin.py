import anvil.http
import urllib.parse
import anvil.secrets
import re

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

  # Einrichten der Abfrageparameter
  params = {
    "key": api_key,
    "cx": cse_id,
    "q": f"site:linkedin.com intitle:\"{full_name}\" {city}",
    "num": 10  # Mehr Ergebnisse anfordern, um nach Filterung noch genug zu haben
  }

  try:
    # Kodieren der Abfrageparameter und Anhängen an die URL
    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{url}?{encoded_params}"

    # HTTP-Anfrage mithilfe der Anvil-Bibliothek mit json=True
    response = anvil.http.request(full_url, method="GET", json=True)

    # Nur die Titel der relevanten Profile extrahieren
    titles = []
    if "items" in response:
      for item in response["items"]:
        title = item.get("title", "")
        # Ausschließen von Titeln, die mit "100+" beginnen und "profiles" enthalten
        if not "profiles | LinkedIn" in title and not "Profile mit dem Suchbegriff" in title:
          titles.append(title)
          # Sobald wir drei Titel haben, brechen wir ab
          if len(titles) >= 3:
            break

    # Rückgabe der Titel mit Zeilenumbruch
    if titles:
      return "\n".join(titles)
    else:
      return None

  except Exception as e:
    print(f"Fehler beim Suchen nach LinkedIn-Profilen: {e}")
    return None


# Beispielanwendung
#full_name = "Dirk Klemer"
#city = "Hamburg"
#title = google_linkedin(full_name, city)
#if title:
#  print(title)