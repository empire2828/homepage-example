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

  params = {
    "key": api_key,
    "cx": cse_id,
    "q": f' {full_name} {city}',
    #"q": f'site:linkedin.com/in/ "{full_name}" {city}',
    #"exactTerms": full_name,
    "num": 10
  }

  try:
    # Kodieren der Abfrageparameter und Anhängen an die URL
    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{url}?{encoded_params}"

    # HTTP-Anfrage mithilfe der Anvil-Bibliothek mit json=True
    response = anvil.http.request(full_url, method="GET", json=True)

    # Debugging
    print("API-Antwort:", response)

    # Nur die Titel der relevanten Profile extrahieren
    results = []
    if "items" in response:
      for item in response["items"]:
        title = item.get("title", "")
        #link = item.get("link", "")
        #snippet = item.get("snippet", "")

        # Nur Ergebnisse mit dem exakten Namen im Titel berücksichtigen
        if full_name.lower() in title.lower():
          # Ausschließen von Suchergebnisseiten und Listenseiten
          if  "profiles | LinkedIn" not in title and "Profile mit dem Suchbegriff" not in title:
            results.append(f"{title}")
            # Sobald wir drei relevante Ergebnisse haben, brechen wir ab
            if len(results) >= 3:
              break

    # Rückgabe der Ergebnisse mit Zeilenumbruch
    if results:
      return "\n".join(results)
    else:
      return f"Keine passenden LinkedIn-Profile für '{full_name}' in {city if city else 'beliebiger Stadt'} gefunden."

  except Exception as e:
    print(f"Fehler beim Suchen nach LinkedIn-Profilen: {e}")
    return f"Fehler bei der Suche: {str(e)}"


# Beispielanwendung
full_name = "Dirk Klemer"
city = "Hamburg"
ergebnisse = google_linkedin(full_name, city)
if ergebnisse:
  print(ergebnisse)