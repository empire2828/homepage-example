import anvil.server


user_has_subscription = False
user_email = None
request_count = 0
current_user = None
multiframe_open = False

def say_hello():
  print("Hello, world")
