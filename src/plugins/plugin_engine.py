from src.plugins.base_plugin import BasePlugin
from src.plugins.result_plugin import ResultPlugin

PLUGIN_LIST = [
    ResultPlugin(),
]

class Plugin(BasePlugin):
    @staticmethod
    def get_plugin(plugin_name: str):
        return PLUGIN_LIST.get(plugin_name, None)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _common_callback(self, event_name, shared_data: dict, method: callable, *args, **kwargs) -> None:
        for plugin in PLUGIN_LIST:
            try:
                # check if the plugin has the event method
                if hasattr(plugin, event_name):
                    plugin.__getattribute__(event_name)(shared_data, method, *args, **kwargs)
            except Exception as e:
                print(f"[PLUGIN ENGINE] Exception in common_callback: {e}")
        
    def on_configure_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_configure_pre_proc', shared_data, method, *args, **kwargs)
        
    def on_configure_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_configure_post_proc', shared_data, method, *args, **kwargs)

    def on_test_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_test_pre_proc', shared_data, method, *args, **kwargs)

    def on_test_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_test_post_proc', shared_data, method, *args, **kwargs)

    def on_flash_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_flash_pre_proc', shared_data, method, *args, **kwargs)

    def on_flash_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_flash_post_proc', shared_data, method, *args, **kwargs)

    def on_command_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_command_pre_proc', shared_data, method, *args, **kwargs)

    def on_command_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_command_post_proc', shared_data, method, *args, **kwargs)

    def on_constraint_check_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_constraint_check_pre_proc', shared_data, method, *args, **kwargs)

    def on_constraint_check_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_constraint_check_post_proc', shared_data, method, *args, **kwargs)

    def on_exception_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_exception_pre_proc', shared_data, method, *args, **kwargs)

    def on_exception_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_exception_post_proc', shared_data, method, *args, **kwargs)

    def on_error_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_error_pre_proc', shared_data, method, *args, **kwargs)

    def on_error_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        self._common_callback('on_error_post_proc', shared_data, method, *args, **kwargs)

