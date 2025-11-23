import anvil.secrets
import anvil.users
from anvil.tables import app_tables
import anvil.server
from anvil import users
import stripe
from datetime import datetime, timedelta, timezone
import hashlib
from servermain import get_bigquery_client, to_sql_value
from google.cloud import bigquery

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

@anvil.server.callable
def get_user_has_subscription_for_email(current_user):
  #current_user = anvil.users.get_user()
  #user = app_tables.users.get(email=email)
  if not current_user:
    return False
  
  subscription_status = current_user.get('subscription')
  if subscription_status in ['Subscription', 'Pro-Subscription', 'Canceled']:
    return True
  else:
    subscription_status = False
  
  tester_status = current_user.get('tester')  
  if tester_status:
    subscription_status = "tester"
    return True  

  print("get_user_has_subscription_for_email: ",current_user['email']," ",subscription_status)
  return False

@anvil.server.callable
def is_user_below_request_count():
  current_user = users.get_user()
  if current_user is None:
    raise Exception("Kein Benutzer angemeldet")
  if not current_user:
    return False
  request_count = current_user.get('request_count')
  if request_count is None or request_count < 5:
    return True
  return False

@anvil.server.callable
def add_request_count(current_user):
  request_count = current_user.get('request_count')
  try:
    request_count = int(request_count)
  except (TypeError, ValueError):
    request_count = 0
  current_user['request_count'] = request_count + 1

  request_count_cum = current_user.get('request_count_cum')
  try:
    request_count_cum = int(request_count_cum)
  except (TypeError, ValueError):
    request_count_cum = 0
  current_user['request_count_cum'] = request_count_cum + 1

  print(" add_request_count: ", current_user['email'], " ", request_count)
  return int(current_user['request_count'])

@anvil.server.callable
def get_request_count():
  current_user = users.get_user()
  if current_user is None:
    raise Exception("Kein Benutzer angemeldet")
  request_count = current_user.get('request_count')
  if request_count is None:
    request_count = 0  
  print(" get_request_count: ",current_user['email']," ",request_count)
  return request_count

@anvil.server.background_task
def reset_request_count_for_all_users():
  for user in app_tables.users.search():
    user['request_count'] = 0

@anvil.server.callable
def trigger_reset_request_count():
  anvil.server.launch_background_task('reset_request_count_for_all_users')

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
def save_user_parameter(std_cleaning_fee=None,
                        std_linen_fee=None,
                        use_own_std_fees=False):
  client = get_bigquery_client()
  user = anvil.users.get_user()
  if not user:
    raise anvil.server.UnauthorizedRequest("No logged-in user")

  email = user["email"]
  supabase_key = user.get("supabase_key", None)

  # Helper to convert empty or invalid strings to floats
  def safe_float(value):
    if value is None or value == "":
      return None
    try:
      return float(value)
    except (TypeError, ValueError):
      return None

  merge_sql = """
      MERGE `lodginia.lodginia.parameter` T
      USING UNNEST([STRUCT(
          @email AS email,
          @std_cleaning_fee AS std_cleaning_fee,
          @std_linen_fee AS std_linen_fee,
          @use_own_std_fees AS use_own_std_fees,
          @supabase_key AS supabase_key
      )]) S
      ON T.email = S.email
      WHEN MATCHED THEN
        UPDATE SET
          std_cleaning_fee = S.std_cleaning_fee,
          std_linen_fee    = S.std_linen_fee,
          use_own_std_fees = S.use_own_std_fees,
          supabase_key     = S.supabase_key
      WHEN NOT MATCHED THEN
        INSERT (email,
                std_cleaning_fee,
                std_linen_fee,
                use_own_std_fees,
                supabase_key)
        VALUES (
          S.email,
          S.std_cleaning_fee,
          S.std_linen_fee,
          S.use_own_std_fees,
          S.supabase_key
        )
    """

  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("email",   "STRING",  email),
      bigquery.ScalarQueryParameter("std_cleaning_fee",  "FLOAT64", safe_float(std_cleaning_fee)),
      bigquery.ScalarQueryParameter("std_linen_fee",  "FLOAT64", safe_float(std_linen_fee)),
      bigquery.ScalarQueryParameter("use_own_std_fees", "BOOL",    bool(use_own_std_fees)),
      bigquery.ScalarQueryParameter("supabase_key",  "STRING",  supabase_key),
    ]
  )

  client.query(merge_sql, job_config=job_config).result()  # DML ⇒ immediately visible
  return True 

# ---------------------------------------------------------------------------
# 2. get_user_parameter  (Pure read)
# ---------------------------------------------------------------------------
@anvil.server.callable
def get_user_parameter():
  client=get_bigquery_client()
  user = anvil.users.get_user()
  if not user:
    return None
  email = user["email"]

  sql = """
      SELECT *
      FROM `lodginia.lodginia.parameter`
      WHERE email = @user_email
      LIMIT 1
    """
  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("user_email", "STRING", email)
    ]
  )
  
  # 4. Run the query and return the first row as a dict (if any).
  rows = list(client.query(sql, job_config=job_config).result())
  anvil.server.call_s('log',str(rows),email="dirk.klemer@gmail.com",function="userfunctions.get_user_parameter")
  return dict(rows[0]) if rows else None

# ---------------------------------------------------------------------------
# 3. save_std_commission  (Upsert via MERGE)
# ---------------------------------------------------------------------------
@anvil.server.callable
def save_std_commission(channel_name=None, channel_commission=None):
  if not channel_name:
    return None

  user = anvil.users.get_user()
  if not user:
    raise anvil.server.UnauthorizedRequest("No logged-in user")

  email         = user["email"]
  supabase_key  = user.get("supabase_key", None)
  commission    = None if channel_commission in ("", None) else float(channel_commission)
  row_id        = f"{email}_{channel_name}"    # composite key

  row_struct = (
    f"STRUCT({to_sql_value(row_id)}        AS id, "
    f"       {to_sql_value(email)}         AS email, "
    f"       {to_sql_value(channel_name)}  AS channel_name, "
    f"       {to_sql_value(commission)}    AS channel_commission, "
    f"       {to_sql_value(supabase_key, force_string=True)}       AS supabase_key)"
  )

  merge_sql = f"""
    MERGE `lodginia.lodginia.std_commission` T
    USING UNNEST([ {row_struct} ]) S
    ON T.email = S.email AND T.channel_name = S.channel_name
    WHEN MATCHED THEN
      UPDATE SET
        channel_commission = S.channel_commission,
        supabase_key       = S.supabase_key
    WHEN NOT MATCHED THEN
      INSERT (id, email, channel_name, channel_commission, supabase_key)
      VALUES(S.id, S.email, S.channel_name, S.channel_commission, S.supabase_key)
    """
  get_bigquery_client().query(merge_sql).result()
  return True

# ---------------------------------------------------------------------------
# 4. save_user_apartment_count  (background task)
# ---------------------------------------------------------------------------
@anvil.server.background_task
def save_user_apartment_count(user_email):
  # 1️⃣ Count distinct, non-null apartments in bookings
  count_sql = """
      SELECT COUNT(DISTINCT apartment) AS c
      FROM `lodginia.lodginia.bookings`
      WHERE email = @user_email
        AND apartment IS NOT NULL
    """
  cfg = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("user_email", "STRING", user_email)]
  )
  count_result = list(get_bigquery_client().query(count_sql, job_config=cfg).result())[0]["c"]

  # 2️⃣ Save back into Anvil table
  user_row = app_tables.users.get(email=user_email)
  if not user_row:
    raise Exception(f"User with email {user_email} not found")
  user_row["apartment_count"] = count_result
  print(f"Apartment count for {user_email}: {count_result}")
  return count_result

# ---------------------------------------------------------------------------
# 5. get_user_channels_from_std_commission  (Pure read)
# ---------------------------------------------------------------------------
@anvil.server.callable
def get_user_channels_from_std_commission(email):
  sql = """
      SELECT channel_name, channel_commission
      FROM `lodginia.lodginia.std_commission`
      WHERE email = @email
      ORDER BY channel_name
    """
  cfg = bigquery.QueryJobConfig(
    query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
  )
  rows = get_bigquery_client().query(sql, job_config=cfg).result()
  return [dict(r) for r in rows]


@anvil.server.callable(require_user=True)
def delete_userparameter_in_bigquery(email):
  client = get_bigquery_client()
  # Table names (change if schema/project differs)
  parameter_table = "lodginia.lodginia.parameter"
  commission_table = "lodginia.lodginia.std_commission"

  queries = [
    (
      f"DELETE FROM `{parameter_table}` WHERE email = @user_email",
      [bigquery.ScalarQueryParameter("user_email", "STRING", email)]
    ),
    (
      f"DELETE FROM `{commission_table}` WHERE email = @user_email",
      [bigquery.ScalarQueryParameter("user_email", "STRING", email)]
    )
  ]

  for sql, params in queries:
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    client.query(sql, job_config=job_config).result()

  return True

@anvil.server.callable(require_user=True)
def delete_user_from_users_table(email):
  # Look up the user row by email
  user_row = app_tables.users.get(email=email)
  if user_row is not None:
    user_row.delete()
    return True
  else:
    return False  # User not found

@anvil.server.callable
def get_my_account_data(email):
  # Lies Parameter und Channel-Daten ggf. aus BigQuery und return sie gebündelt!
  params = get_user_parameter()
  channels = get_user_channels_from_std_commission(email)
  return {"params": params, "channels": channels}