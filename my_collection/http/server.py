import fastapi

from my_collection.http.context import Context


async def exception_handler(r: fastapi.Request, e: Exception):
    if isinstance(e, fastapi.HTTPException):
        return fastapi.responses.JSONResponse(
            status_code=e.status_code,
            content={"msg": e.detail},
        )
    else:
        return fastapi.responses.JSONResponse(
            status_code=500,
            content=e.__repr__(),
        )


class Server:
    app: fastapi.FastAPI

    def __init__(self, ctx: Context):
        self.app = fastapi.FastAPI()
        self.ctx = ctx
        self.__init_server()

    def __init_server(self):
        self.app.exception_handler(Exception)(exception_handler)
        for (method, path), func_name in self.ctx.method_dict.items():
            if method == self.ctx.method_get:
                self.app.get(path)(self.__getattribute__(func_name))
            if method == self.ctx.method_post:
                self.app.post(path)(self.__getattribute__(func_name))
            if method == self.ctx.method_put:
                self.app.put(path)(self.__getattribute__(func_name))
            if method == self.ctx.method_delete:
                self.app.delete(path)(self.__getattribute__(func_name))
