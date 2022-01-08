import asyncio
from typing import Optional

import fastapi
import uvicorn

from my_collection import http

router = http.Router()


class Server(http.Server):
    def __init__(self):
        super(Server, self).__init__(router)

    @router.http_method(router.method_get, "/hello/{path}")
    def hello(
            self,
            path: Optional[str] = fastapi.Path(default=None),
            name: Optional[str] = fastapi.Query(default=None),
    ):
        return f"hello {name} from {path}"


if __name__ == "__main__":
    uvicorn.run(Server().app, host="localhost", port=3000, loop="asyncio")
