import anvil.server

user_has_subscription = False
user_email = None
request_count = 0
current_user = None

def testen_button():
  global request_count, user_has_subscription, current_user
  user = anvil.users.signup_with_form(allow_cancel=True)
  if user:
    anvil.server.call("create_supabase_key")
    anvil.server.call("send_registration_notification", user["email"])
    # Layout Template öffnen
    current_user = user
    request_count = 0
    user_has_subscription= False
    layout_form = open_form("layout_template")
    # Dashboard automatisch laden
    layout_form.reset_links()
    layout_form.dashboard_navigation_link.selected = True   
    multiframe_form = layout_form.open_multiframe_form()
    multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
    # Navigation Link als aktiv markieren
