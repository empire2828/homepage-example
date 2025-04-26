from routing.router import Route, debug_logging

debug_logging(True)

class homepageRoute(Route):
    path = "/"
    form = "homepage"

class data_protectionRoute(Route):
    path = "/data_protection"
    form = "data_protection"


