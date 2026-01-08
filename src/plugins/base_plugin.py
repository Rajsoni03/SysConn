from abc import ABC, abstractmethod
import functools

# Helper function to extract shared_data from args or kwargs
def get_shared_data(*args, **kwargs):
    shared_data = {}
    if len(args) > 0:
        shared_data = args[0]
    elif "shared_data" in kwargs:
        shared_data = kwargs["shared_data"]
    else:
        kwargs["shared_data"] = shared_data
    return shared_data


class BasePlugin(ABC):
    '''
    Base class for all plugins. All plugins must inherit from this class and implement the abstract methods.
    on_<event> methods will be called at various stages of the test execution process.
    '''
    
    @staticmethod
    def common_wrapper(method: callable, pre_proc: callable, post_proc: callable) -> callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            shared_data = get_shared_data(*args, **kwargs)
            pre_proc(shared_data, method, *args, **kwargs)
            result = method(self, shared_data, *args, **kwargs)
            post_proc(shared_data, method, *args, **kwargs)
            return result
        return wrapper

    def on_configure(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_configure_pre_proc,
                                            self.on_configure_post_proc)
        return wrapper
    
    def on_test(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_test_pre_proc,
                                            self.on_test_post_proc)
        return wrapper

    def on_flash(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_flash_pre_proc,
                                            self.on_flash_post_proc)
        return wrapper

    def on_command(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_command_pre_proc,
                                            self.on_command_post_proc)
        return wrapper

    def on_constraint_check(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_constraint_check_pre_proc,
                                            self.on_constraint_check_post_proc)
        return wrapper

    def on_exception(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_exception_pre_proc,
                                            self.on_exception_post_proc)
        return wrapper

    def on_error(self, method) -> callable:
        wrapper = BasePlugin.common_wrapper(method,
                                            self.on_error_pre_proc,
                                            self.on_error_post_proc)
        return wrapper
    
    
    # Abstract methods for pre and post processing
    @abstractmethod
    def on_configure_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_configure_pre_proc method.")
    
    @abstractmethod
    def on_configure_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_configure_post_proc method.")
    
    @abstractmethod
    def on_test_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_test_pre_proc method.")
    
    @abstractmethod
    def on_test_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_test_post_proc method.")
    
    @abstractmethod
    def on_flash_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_flash_pre_proc method.")
    
    @abstractmethod
    def on_flash_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_flash_post_proc method.")
    
    @abstractmethod
    def on_command_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_command_pre_proc method.")
    
    @abstractmethod
    def on_command_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_command_post_proc method.")
    
    @abstractmethod
    def on_constraint_check_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_constraint_check_pre_proc method.")
    
    @abstractmethod
    def on_constraint_check_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_constraint_check_post_proc method.")
    
    @abstractmethod
    def on_exception_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_exception_pre_proc method.")
    
    @abstractmethod
    def on_exception_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_exception_post_proc method.")
    
    @abstractmethod
    def on_error_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_error_pre_proc method.")
    
    @abstractmethod
    def on_error_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        raise NotImplementedError("Subclass must implement the on_error_post_proc method.")