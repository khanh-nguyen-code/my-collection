from typing import Dict, Tuple, Callable


class Context:
    method_get: str = "get"
    method_post: str = "post"
    method_put: str = "put"
    method_delete: str = "delete"

    def __init__(self):
        self.method_dict: Dict[Tuple[str, str], str] = {}  # (method, path) -> func_name

    def http_method(self, method: str, path: str):
        def helper(func: Callable) -> Callable:
            self.method_dict[(method, path)] = func.__name__
            return func

        return helper
