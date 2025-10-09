from routing.router import Route #, debug_logging

# debug_logging(True)

class homepage_route(Route):
    path = "/"
    form = "homepage"
    #cache_form = True
    #cache_data = True

class data_protection_route(Route):
    path = "/data_protection"
    form = "data_protection"

class knowledge_hub(Route):
  path = "/knowledge_hub"
  form = "knowledge_hub"