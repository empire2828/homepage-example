import anvil.email
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import users
import stripe
from datetime import datetime, timedelta, timezone

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = anvil.secrets.get_secret('stripe_secret_api_key')

# @anvil.server.callable's require_user argument takes either a Boolean value. If the Boolean is True, the user has permission to run the decorated function.
# We can pass require_user a function which evaluates to True or False but we cannot pass any arguments to that function
# To get around this, we can pass require_user a higher order function - user_has_subscription - which returns an evaluated function verify_subscription
# user_has_subscription can accept arguments, use them in verify_subscription and return the evaluated verify_subscription function
# so, if we call @anvil.server.callable(require_user=user_has_subscription(["pro"])), the decorator calls user_has_subscription which returns an evaluated function object that require_user can use
# verify_subscription receives the currently logged-in user object from @anvil.server.callable automatically
# See the Product Server Module to see it in use

#old
#def user_has_subscription(allowed_subscriptions):
#    def verify_subscription(user):
#        # Return true if user has subscription in allowed subscriptions
#        return user["subscription"] and user["subscription"].lower() in [subscription.lower() for subscription in allowed_subscriptions]
#    return verify_subscription

#@anvil.server.callable
#def user_has_subscription(allowed_subscriptions):
#    def verify_subscription(user):
#        # Check if the user has a valid subscription
#        if user["subscription"] and user["subscription"].lower() in [subscription.lower() for subscription in allowed_subscriptions]:
#            return True
#              # Check if the user is within their 30-day free trial period
#        if "first_login_date" in user:
#            first_login_date = datetime.strptime(user["signed_up"], "%Y-%m-%d")
#            if datetime.now() <= first_login_date + timedelta(days=30):
#                return True       
#        # If neither condition is met, return False
#        return False

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
    if user['subscription'] == 'Personal':    
        return True   
    signed_up_date = user['signed_up']  # Verwende get() für Sicherheit    
    if signed_up_date:
        # Konvertiere naive Zeit zu UTC-aware Zeit
        signed_up_aware = signed_up_date.replace(tzinfo=timezone.utc)
        trial_end = signed_up_aware + timedelta(days=5)
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
    user_row['pms_api_key'] = api_key
    
    return True