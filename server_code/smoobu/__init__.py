import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets
import json

def get_guest_details(guestid, headers):
    """Ruft die Gästedaten für einen bestimmten Gast ab"""
    guest_url = f"https://login.smoobu.com/api/guests/{guestid}"
    
    response = requests.get(guest_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 422:
        print(f"Gast nicht gefunden für ID: {guestid}")
        return {}  # Leeres Dictionary zurückgeben, wenn der Gast nicht gefunden wurde
    else:
        print(f"Fehler beim Abrufen der Gästedaten: {response.status_code} - {response.text}")
        return {}  # Leeres Dictionary für andere Fehler zurückgeben

def get_smoobu_userid(user_email):
  user= app_tables.users.get(email=user_email)
  if user:
        api_key= user['pms_api_key']
  else:
    pass
    headers = {
        "Api-Key": api_key,
        "Cache-Control": "no-cache"
    }
  
    response = requests.get("https://login.smoobu.com/api/me", headers=headers)
  
    if response.status_code == 200:
        data = response.json()
        return data['id']
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

