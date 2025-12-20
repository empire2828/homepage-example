import anvil.server

# Initialisierung aller globalen Variablen
current_user = None
current_multiframe_instance = None
multiframe_open = False
user_has_subscription = None
request_count = 0

def say_hello():
  print("Hello, world")
