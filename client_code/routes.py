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

class data_protection_route(Route):
    path = "/data_protection"
    form = "data_protection"

class knowledge_hub(Route):
  path = "/knowledge_hub"
  form = "knowledge_hub"

class cancellations_de(Route):
  path = "/stornierungen_analytisch_vermeiden"
  form = "blog.cancellations_de"

class cancellations_en(Route):
  path = "/how_to_avoid_cancellations_analytical"
  form = "blog.cancellations_en"