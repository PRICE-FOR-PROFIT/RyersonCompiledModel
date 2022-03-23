from .welcome import WelcomeApi


def initialize_routes(api):
    api.add_resource(WelcomeApi, '/api/welcome')

