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

# Client außerhalb der Funktion initialisieren, damit er für alle Funktionen verfügbar ist
client = OpenAI(
  api_key=anvil.secrets.get_secret('PERPLEXITY_API_KEY'),
  base_url="https://api.perplexity.ai"
)

@anvil.server.callable
def screener_open_ai(name, location, checktype):
  if checktype == "job":
    prompt = f"""
Welchen beruf hat {name} bei einem unternehmen in der nähe von {location}? Wenn kein Beruf bekannt ist, wo ist er oder sie in der nähe von {location} in Erscheinung getreten? Schreibe extrem kurz ohne Zitatnummern.
"""
  else:
    prompt = f"""
Schätze das Alter von {name} aus {location} anhand des beruflichen Werdeganges und ob z.B. Kinder vorhanden sind sehr grob ein. Schreibe als Antwort nur: von bis Jahre und lasse alles andere weg.
"""
    
  try:
    response = client.chat.completions.create(
      model="sonar",
      messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": name},  
      ],
      max_tokens=128,
      temperature=0.5,
      top_p=0.9,
      stream=False,
      presence_penalty=0,
      frequency_penalty=0,
      response_format=None
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"Fehler: {e}"

