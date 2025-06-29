#import anvil.email
import anvil.secrets
import anvil.users
from anvil.tables import app_tables
import anvil.server
from anvil import users
import stripe
from datetime import datetime, timedelta, timezone

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


