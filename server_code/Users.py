import anvil.secrets
import anvil.users
from anvil.tables import app_tables
import anvil.server
from anvil import users
import stripe
from datetime import datetime, timedelta, timezone
import hashlib
from supabase import create_client, Client

supabase_url = "https://huqekufiyvheckmdigze.supabase.co"
supabase_api_key = anvil.secrets.get_secret('supabase_api_key')
supabase_client: Client = create_client(supabase_url, supabase_api_key)

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = anvil.secrets.get_secret('stripe_secret_api_key')

@anvil.server.callable(require_user=True)
def change_name(name):
  user = anvil.users.get_user()
  user["name"] = name
  return user

@anvil.server.callable(require_user=True)
def change_email(email):
  user = anvil.users.get_user()
  try:
    customer = stripe.Customer.modify(
        user["stripe_id"],
        email=email
    )
    user["email"] = email
    print("Customer email updated successfully:", customer)
  except stripe.error.StripeError as e:
      print("Stripe API error:", e)
  except Exception as e:
      print("An error occurred when updating a user's email:", e)
  return user

@anvil.server.callable(require_user=True)
def delete_user():
  user = anvil.users.get_user()
  if user["stripe_id"]:
    try: 
      deleted_customer = stripe.Customer.delete(user["stripe_id"])
      user.delete()
      print(f"Customer {user['stripe_id']} deleted successfully:", deleted_customer)
    except stripe.error.StripeError as e:
      print("Stripe API error:", e)
    except Exception as e:
      print("An unexpected error occurred:", e)
  else:
    user.delete()

@anvil.server.callable(require_user=True)
def send_password_reset_email():
    try:
        # Get the email of the currently logged-in user
        user_email = anvil.users.get_user()['email']
                # Send the password reset email
        anvil.users.send_password_reset_email(user_email)
        return "Password reset email sent successfully."
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return "Failed to send password reset email."

# Server-Modul DKL
@anvil.server.callable
def get_user_has_subscription():
    user = anvil.users.get_user()    
    if not user:
        return False   
    if user['subscription'] == ('Subscription' or 'Pro-Subscription' or 'Canceled'):    
        return True   
    signed_up_date = user['signed_up']  
    if signed_up_date:
        # Konvertiere naive Zeit zu UTC-aware Zeit
        signed_up_aware = signed_up_date.replace(tzinfo=timezone.utc)
        trial_end = signed_up_aware + timedelta(days=30)
        now_utc = datetime.now(timezone.utc)  # Korrekte UTC-Zeit
        return now_utc <= trial_end   
    return False

@anvil.server.callable
def save_user_api_key(api_key):
    # Den aktuellen Benutzer abrufen
    current_user = users.get_user()
    
    if current_user is None:
        raise Exception("Kein Benutzer angemeldet")
    
    # Den Benutzer in der Datenbank finden und aktualisieren
    user_row = app_tables.users.get(email=current_user['email'])
    
    if user_row is None:
        raise Exception("Benutzer nicht in der Datenbank gefunden")
    
    # API-Key in der Datenbank speichern
    user_row['smoobu_api_key'] = api_key
    
    return True
  
@anvil.server.callable
def create_supabase_key():
  # E-Mail in Kleinbuchstaben umwandeln und als Bytes kodieren
  user = anvil.users.get_user()
  if user is not None:
    email = user['email']
  lowercase_email = email.lower().encode('utf-8')
  # SHA-256-Hash berechnen
  hash_digest = hashlib.sha256(lowercase_email).hexdigest()
  # Die ersten 12 Zeichen des Hashs als Zahl interpretieren (z. B. als int im Hex-Format)
  key = str(int(hash_digest[:12], 16))
  user['supabase_key']=key
  return 

@anvil.server.callable
def save_user_parameter(std_cleaning_fee=None, std_linen_fee=None,use_own_std_fees=False):
  current_user = anvil.users.get_user()
  email = current_user['email']
  supabase_key = current_user['supabase_key']
  data = {
    "supabase_key": supabase_key,
    "std_cleaning_fee": std_cleaning_fee,
    "std_linen_fee": std_linen_fee,
    "use_own_std_fees": use_own_std_fees,
    "email": email
  }
  response = supabase_client.table("parameter").upsert(
    [data],
    on_conflict="email"  # Konfliktspalte angeben!
  ).execute()
  return response.data  # oder True/False je nach Bedarf
  pass

@anvil.server.callable
def get_user_parameter():
  current_user = anvil.users.get_user()
  if not current_user:
    return None  # No user is logged in
  email = current_user['email']
  # Fetch the parameter entry from Supabase by email
  response = supabase_client.table("parameter").select("*").eq("email", email).execute()
  if response.data:
    # Return the first matching item (should be unique based on email)
    return response.data[0]
  else:
    return None  # No parameter found for user

@anvil.server.callable
def save_std_commission(channel_name=None, channel_commission=None):
  current_user = anvil.users.get_user()
  email = current_user['email']
  supabase_key = current_user['supabase_key']
  if channel_commission == "" or channel_commission is None:
    channel_commission_value = None
  else:
    channel_commission_value = float(channel_commission)  
  if not channel_name:
    return None  # oder False, je nach Bedarf
  data = {
    "channel_name": channel_name,
    "channel_commission": channel_commission_value,
    "supabase_key": supabase_key,
    "email": email
  }
  print('std_commissions saved',data)
  response = supabase_client.table("std_commission").upsert(
    [data],
    on_conflict="email, channel_name"  # Konfliktspalte angeben!
  ).execute()
  return response.data  # oder True/False je nach Bedarf
  pass

@anvil.server.background_task
def save_user_apartment_count(user_email):
  # Step 1: Hole alle Buchungen für den Nutzer (es werden alle mit "apartment" geladen)
  response = (
    supabase_client
      .table("bookings")
      .select("apartment")
      .eq("email", user_email)
      .execute()
  )
  # Apartments aus Zeilen mit Wert extrahieren (keine Nulls)
  apartments = [row['apartment'] for row in response.data if row.get('apartment')]
  unique_apartments = set(apartments)
  count = len(unique_apartments)

  # Step 2: User-Row in Anvil-Table finden und speichern
  user_row = app_tables.users.get(email=user_email)
  if user_row is not None:
    user_row['apartment_count'] = count
    print(f"Apartment count for {user_email}: {count}")
    return count
  else:
    raise Exception(f"User with email {user_email} not found")

@anvil.server.callable
def get_user_channels_from_std_commission(email):
  r = supabase_client.table('std_commission')\
    .select('channel_name, channel_commission').eq('email', email).execute()
  return r.data  # Sollte eine Liste von Dicts sein!

