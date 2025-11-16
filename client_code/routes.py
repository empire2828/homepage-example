from routing.router import Route 

class homepage_route(Route):
    path = "/"
    form = "home.home_start"

class home_de(Route):
  path = "/de"
  form = "home.home_de"

class home_en(Route):
  path = "/en"
  form = "home.home_en"

class channel_manager_connect(Route):
  path = "/channel_manager_connect"
  form = "channel_manager_connect"

class blog_de(Route):
  path = "/blog_de"
  form = "blog.blog_de"

class blog_en(Route):
  path = "/blog_en"
  form = "blog.blog_en"

class data_protection_route(Route):
    path = "/data_protection"
    form = "home.data_protection"

class knowledge_hub(Route):
  path = "/knowledge_hub"
  form = "knowledge_hub"

class cancellations_de(Route):
  path = "/stornierungen_analytisch_vermeiden"
  form = "blog.cancellations_de"

class cancellations_en(Route):
  path = "/how_to_avoid_cancellations_analytical"
  form = "blog.cancellations_en"

class stly_de(Route):
  path = "/warum_vergleiche_des_buchungsstandes_in_smoobu_gefaehrlich_sind"
  form = "blog.stly_de"

class stly_en(Route):
  path = "/why_comparing_booking_status_in_smoobu_is_dangerous"
  form = "blog.stly_en"