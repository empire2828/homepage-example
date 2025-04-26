from routing.router import Route, debug_logging

debug_logging(True)

class homepage(Route):
    path = "/"
    form = "homepage"

class data_protection(Route):
    path = "/data_protection"
    form = "data_protection"


