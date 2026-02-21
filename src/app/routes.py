from api.common.default import Home, SetConfig, Version, Update, HealthCheck
from api.common.log import Logs

from api.v1.workarea import Workarea
from api.v1.command import Command
from api.v1.test import RunTest, TestStatus
from api.v1.uart import ListUart

from config.settings import API_VERSIONS

API_ROUTES = {
    "common": [
        ('/', Home),
        ('/set_config', SetConfig),
        ('/version', Version),
        ('/update', Update),
        ('/health', HealthCheck),
        ('/logs/<path:filepath>', Logs)
    ],
    "v1": [
        ('/api/v1/workarea', Workarea),
        ('/api/v1/command', Command),
        ('/api/v1/uart/list', ListUart),
        ('/api/v1/test/run', RunTest), 
        ('/api/v1/test/status/<string:id>', TestStatus),
    ],
    "v2": [
        # Future v2 routes can be added here
    ]
}

def register_routes(api):
    for version in API_VERSIONS:
        for route, resource in API_ROUTES.get(version, []):
            api.add_resource(resource, route)