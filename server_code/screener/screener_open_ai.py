import anvil.secrets
import anvil.server
from openai import OpenAI
from linkup import LinkupClient  # Changed import

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



# Initialize Linkup client########################################################################################
client = LinkupClient(
  api_key=anvil.secrets.get_secret('linkup_api_key')  # Make sure to store this in Anvil secrets
)

@anvil.server.callable
def screener_open_ai(name, location, checktype):
  location = location or ""  # Handle None location

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
    # Execute Linkup search instead of OpenAI call
    response = client.search(
      query=query,
      depth="deep",  # For comprehensive results
      output_type="sourcedAnswer"  # Get structured answer with sources
    )

    return response['answer']  # Access the answer directly from response

  except Exception as e:
    return f"Fehler: {e}"

