from routing.router import Route, debug_logging

debug_logging(True)

class homepage_route(Route):
    path = "/"
    form = "homepage"

class data_protection_route(Route):
    path = "/data_protection"
    form = "data_protection"

class daashboard_route(Route):
    path = "/dashboard"
    form = "dashboard"

