import anvil.files
from anvil.files import data_files
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from openai import OpenAI

# Prüfe, ob die API-Key-Schlüssel korrekt sind
client = OpenAI(
  api_key=anvil.secrets.get_secret('PERPLEXITY_API_KEY'),
  base_url="https://api.perplexity.ai"
)

@anvil.server.callable
def open_ai(name, location, checktype):
  if checktype == "job":
    prompt = f"""
Welchen beruf hat {name} bei einem unternehmen in der nähe von {location}? Wenn kein Beruf bekannt ist, Wo ist Sie in der nähe von {location} in Erscheinung getreten? Schreibe sehr kurz ohne Zitatnummern.
"""
  else:
    prompt = f"""
Schätze das Alter von {name} aus {location} anhand des beruflichen Werdeganges und ob z.B. Kinder vorhanden sind sehr grob ein. Schreibe als Antwort nur: von bis Jahre und lasse alles andere weg.
"""
    
  # Prüfe, ob der Client korrekt initialisiert wurde
  try:
    response = client.chat.completions.create(
      model="sonar-pro",
      messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": name},  
      ],
    )
    return response.choices[0].message.content
  except Exception as e:
    # Fange potenzielle Fehler ab
    return f"Fehler: {e}"

# print(open_ai("Andrea Querner","Dresden","job"))
# test from github vs studio
