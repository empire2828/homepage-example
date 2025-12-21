import anvil.server

current_multiframe_instance = None
user_has_subscription = None
user_email = None
request_count = 0
current_user = None
multiframe_open = False

def say_hello():
  print("Hello, world")
