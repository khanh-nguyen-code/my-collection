from typing import Optional

import fastapi
import uvicorn

from my_collection import http

ctx = http.Context()


class Server(http.Server):
    def __init__(self):
        super(Server, self).__init__(ctx)

    @ctx.http_method(ctx.method_get, "/hello/{path}")
    def hello(
            self,
            path: Optional[str] = fastapi.Path(default=None),
            name: Optional[str] = fastapi.Query(default=None),
    ):
        return f"hello {name} from {path}"


if __name__ == "__main__":
    uvicorn.run(Server().app, host="localhost", port=3000)
