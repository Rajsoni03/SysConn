# Plugin System

SysConn includes an extensible plugin system that lets you inject custom logic
at key points in the test lifecycle without modifying core code.

---

## Architecture

```
TestExecutorService
  └─ TestFlow.execute()
        ├─ PluginEngine.before_test(test_data)
        │     └─ plugin.before_test() for each registered plugin
        ├─ [test steps run]
        ├─ PluginEngine.after_test(test_data, result)
        │     └─ plugin.after_test() for each registered plugin
        └─ PluginEngine.on_error(test_data, error)  (on failure)
              └─ plugin.on_error() for each registered plugin
```

Plugins are discovered by the `PluginEngine` and called in registration order.

---

## BasePlugin (`src/plugins/base_plugin.py`)

All plugins extend `BasePlugin` and override the hooks they need:

```python
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):

    def before_test(self, test_data: dict) -> None:
        """Called once before any test step runs."""
        print(f"Starting test {test_data.get('jira_id')}")

    def after_test(self, test_data: dict, result: dict) -> None:
        """Called once after all steps complete successfully."""
        print(f"Test passed: {result}")

    def on_error(self, test_data: dict, error: Exception) -> None:
        """Called if any step raises an exception."""
        print(f"Test failed: {error}")
```

Hooks you do not override are no-ops by default.

---

## Lifecycle Hooks

| Hook | Signature | When called |
|------|-----------|-------------|
| `before_test` | `(test_data: dict)` | Before the first test step |
| `after_test` | `(test_data: dict, result: dict)` | After the last step succeeds |
| `on_error` | `(test_data: dict, error: Exception)` | If any step raises |

---

## PluginEngine (`src/core/`)

The engine maintains a list of plugin instances and dispatches lifecycle events:

```python
from src.core.plugin_engine import PluginEngine

engine = PluginEngine()
engine.register(MyPlugin())
engine.register(ResultPlugin())

engine.before_test(test_data)
# ...
engine.after_test(test_data, result)
```

---

## Built-in Plugins

### ResultPlugin (`src/plugins/result_plugin.py`)

Records test results to the TinyDB database after each test run.
Always registered by the test executor — do not remove it.

---

## Writing a Custom Plugin

1. Create `src/plugins/my_plugin.py`:

```python
from src.plugins.base_plugin import BasePlugin
import requests

class JiraNotifierPlugin(BasePlugin):
    """Posts a comment to the Jira ticket when a test finishes."""

    def after_test(self, test_data: dict, result: dict) -> None:
        jira_id = test_data.get("jira_id")
        if not jira_id:
            return
        requests.post(
            f"https://jira.example.com/rest/api/2/issue/{jira_id}/comment",
            json={"body": f"Test completed: {result}"},
            auth=("user", "pass"),
        )

    def on_error(self, test_data: dict, error: Exception) -> None:
        jira_id = test_data.get("jira_id")
        if not jira_id:
            return
        requests.post(
            f"https://jira.example.com/rest/api/2/issue/{jira_id}/comment",
            json={"body": f"Test failed: {error}"},
            auth=("user", "pass"),
        )
```

2. Register it in the test executor or in `app.py`:

```python
from src.plugins.my_plugin import JiraNotifierPlugin

plugin_engine.register(JiraNotifierPlugin())
```

---

## Notes

- Plugins run in the test execution thread, not the request thread.
- Exceptions raised inside a plugin hook are caught and logged; they do not
  propagate to the test flow unless re-raised intentionally.
- Plugin registration order determines call order.
- Plugins share the same `test_data` dict — mutations are visible to later plugins.
