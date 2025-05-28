import anvil.secrets
import anvil.server
from openai import OpenAI

import urllib.request
import urllib.parse
import json

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
def screener_open_ai_old(name, location, checktype):
  if location is None:
    location=""
  location = location
  if checktype == "job":
    prompt = """
    1. Welchen Beruf hat die Person? Schaue auch bei linkedin und Xing. 
    2. Welches Hobby hat die Person? 
    3. Schreibe sehr kurz mit wenig Wörtern.
    4. Lasse Zitatnummern weg.
    5. Wichtig: Keine Daten vor 1970"""   
  else:
    prompt = f"""
Schätze das Alter von {name} aus {location} anhand des beruflichen Werdeganges und ob z.B. Kinder vorhanden sind sehr grob ein. Schreibe als Antwort nur: von bis Jahre und lasse alles andere weg.
"""
    
  try:
    response = client.chat.completions.create(
      model="sonar",
      #model="sonar-pro",
      #model="gpt-4o-mini",
      #model="gemini-2.0-flash",
      messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": name + " aus " +location},  
      ],
      max_tokens=150,
      temperature=0.5,
      top_p=0.9,
      #stream=False,
      #presence_penalty=0,
      #frequency_penalty=0,
      response_format=None
    )
    #time.sleep(5)
    return response.choices[0].message.content
  except Exception as e:
    return f"Fehler: {e}"





@anvil.server.callable
def screener_open_ai(name, location, checktype):
  location = location or ""  # Handle None location

  # Get API key from Anvil secrets
  api_key = anvil.secrets.get_secret('linkup_api_key')

  # Construct queries based on checktype
  if checktype == "job":
    query = f"""
        Find professional information about {name} from {location}. Include:
        1. Welchen Beruf hat die Person? Schaue auch bei linkedin und Xing. 
        2. Welches Hobby hat die Person? 
        3. Schreibe sehr kurz mit wenig Wörtern.
        4. Lasse Zitatnummern weg.
        5. Wichtig: Keine Daten vor 1970   
        """
  else:
    query = f"""
        Estimate approximate age range of {name} from {location} based on:
        - Career progression timeline
        - Family status (e.g., presence of children)
        Respond ONLY with format: 'XX-XX Jahre' without additional text
        """

  try:
    # Setup request data
    data = {
      "q": query,
      "depth": "deep",
      "outputType": "sourcedAnswer"
    }

    # Convert data to JSON and encode
    json_data = json.dumps(data).encode('utf-8')

    # Create request
    request = urllib.request.Request(
      'https://api.linkup.so/v1/search',
      data=json_data,
      headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
      }
    )

    # Make API request
    with urllib.request.urlopen(request) as response:
      result = json.loads(response.read().decode('utf-8'))
      return result.get('answer', 'Keine Antwort erhalten')

  except urllib.error.HTTPError as e:
    return f"HTTP-Fehler: {e.code} - {e.reason}"
  except Exception as e:
    return f"Fehler: {e}"

