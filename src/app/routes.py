from api.common.default import Home, SetConfig, Version, Update, HealthCheck
from api.common.log import Logs

from api.v1.workarea import Workarea
from api.v1.command import Command
from api.v1.run_test import RunTest
from api.v1.uart import ListUart

from src.app.settings import API_VERSIONS

API_ROUTES = {
    "common": [
        ('/', Home),
        ('/set_config', SetConfig),
        ('/version', Version),
        ('/update', Update),
        ('/health', HealthCheck),
        ('/logs', Logs)
    ],
    "v1": [
        ('/api/v1/workarea', Workarea),
        ('/api/v1/command', Command),
        ('/api/v1/run_test', RunTest),
        ('/api/v1/uart/list', ListUart)
    ],
    "v2": [
        # Future v2 routes can be added here
    ]
}

def register_routes(api):
    for version in API_VERSIONS:
        for route, resource in API_ROUTES.get(version, []):
            api.add_resource(resource, route)