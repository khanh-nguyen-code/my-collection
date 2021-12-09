from typing import Dict, Tuple, Callable, Any, List

import pydantic

Method = Tuple[str, str]


class MethodConfig(pydantic.BaseModel):
    handler_name: str
    args: List[Any]
    kwargs: Dict[str, Any]


class Context:
    """
    description of a http server
    """
    method_get: str = "get"
    method_post: str = "post"
    method_put: str = "put"
    method_delete: str = "delete"

    def __init__(self):
        self.method_dict: Dict[Method, MethodConfig] = {}  # (method, path) -> method_config

    def http_method(self, method: str, path: str, *args, **kwargs):
        def helper(func: Callable) -> Callable:
            self.method_dict[(method, path)] = MethodConfig(handler_name=func.__name__, args=args, kwargs=kwargs)
            return func

        return helper
