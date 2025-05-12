#import anvil.google.auth, anvil.google.drive, anvil.google.mail
#from anvil.google.drive import app_files
#import anvil.email
import anvil.secrets
#import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from openai import OpenAI
#import time

# Client außerhalb der Funktion initialisieren, damit er für alle Funktionen verfügbar ist
client = OpenAI(
  #api_key=anvil.secrets.get_secret('openai_api_key'),
  #api_key=anvil.secrets.get_secret('gemini_api_key'),
  api_key=anvil.secrets.get_secret('PERPLEXITY_API_KEY'),
  #base_url="https://api.openai.com/v1/"
  base_url="https://api.perplexity.ai"
  #base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@anvil.server.callable
def screener_open_ai(name, location, checktype):
  if location is None:
    location=""
  location = location
  if checktype == "job":
    prompt = "1. Welchen Beruf und welches Hobby hat die Person? 2. Schreibe extrem kurz mit sehr wenig Wörtern 3. Lasse Zitatnummern weg. 4. Lasse Bezüge weg 5. Suche auch bei linkedin"
  else:
    prompt = f"""
Schätze das Alter von {name} aus {location} anhand des beruflichen Werdeganges und ob z.B. Kinder vorhanden sind sehr grob ein. Schreibe als Antwort nur: von bis Jahre und lasse alles andere weg.
"""
    
  try:
    response = client.chat.completions.create(
      model="sonar-pro",
      #model="gpt-4o-mini",
      #model="gemini-2.0-flash",
      messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": name + " aus " +location},  
      ],
      max_tokens=150,
      #temperature=0.5,
      #top_p=0.9,
      #stream=False,
      #presence_penalty=0,
      #frequency_penalty=0,
      response_format=None
    )
    #time.sleep(5)
    return response.choices[0].message.content
  except Exception as e:
    return f"Fehler: {e}"

