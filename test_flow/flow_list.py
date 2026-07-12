from test_flow.command_line import CommandLineTestFlow
from test_flow.example import ExampleTestFlow

FLOW_ROUTES = {
    'example': ExampleTestFlow(),
    'command_line': CommandLineTestFlow(),
}
