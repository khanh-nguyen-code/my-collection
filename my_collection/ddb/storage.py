from __future__ import annotations

import base64
import json
import os
from functools import reduce
from typing import Any, Dict

import dill
import fastapi
import pydantic

from my_collection import http
from my_collection.buffer_db import DB
from my_collection.transform import t_map, t_filter


class TransformRequest(pydantic.BaseModel):
    transform_func: str  # base64 of transform.Transform
    reduce_func: str  # base64 of Callable[[Any, Any], Any]
    reduce_init: Any


ctx = http.Context()


class Storage(http.Server):
    def __init__(self, db_path: str):
        super(Storage, self).__init__(ctx)
        if not os.path.exists(db_path):
            open(db_path, "wb").close()
        self.file = open(db_path, "r+b")
        self.db = DB(self.file)

    @ctx.http_method(ctx.method_get, "/query/{path:path}")
    async def get(self,
                  path: str = fastapi.Path(default=None),
                  key: str = fastapi.Query(default=None),
                  ):
        with self.db.context() as db_ctx:
            b = db_ctx.read(f"{path}?key={key}")
            if b is None:
                return None
            return json.loads(b.decode("utf-8"))

    @ctx.http_method(ctx.method_post, "/query/{path:path}")
    async def post(self,
                   path: str = fastapi.Path(default=None),
                   key: str = fastapi.Query(default=None),
                   val: Any = fastapi.Body(default=None),
                   ):
        with self.db.context() as db_ctx:
            db_ctx.write(f"{path}?key={key}", json.dumps(val).encode("utf-8"))
        self.file.flush()

    @ctx.http_method(ctx.method_delete, "/query/{path:path}")
    async def delete(self,
                     path: str = fastapi.Path(default=None),
                     key: str = fastapi.Query(default=None),
                     ):
        with self.db.context() as db_ctx:
            db_ctx.delete(f"{path}?key={key}")
        self.file.flush()

    @ctx.http_method(ctx.method_post, "/transform/{path:path}")
    async def transform(self,
                        path: str = fastapi.Path(default=None),
                        t: TransformRequest = fastapi.Body(default=None),
                        ):
        transform_func = dill.loads(base64.b64decode(t.transform_func))
        reduce_func = dill.loads(base64.b64decode(t.reduce_func))
        with self.db.context() as db_ctx:
            @t_filter
            def key_filter(key: str) -> bool:
                return key.split("?")[0] == path

            @t_map
            def key_to_val(key: str) -> Any:
                return json.loads(db_ctx.read(key).decode("utf-8"))

            func = transform_func * key_to_val * key_filter
            out = reduce(reduce_func, func(db_ctx.keys()), t.reduce_init)
            print(db_ctx.keys(), out)
            return out

    @ctx.http_method(ctx.method_get, "/file/{path:path}")
    async def read(self,
                   path: str = fastapi.Path(default=None),
                   ):
        with self.db.context() as db_ctx:
            out = {}
            for key in db_ctx.keys():
                if key.split("?")[0] != path:
                    continue
                b = db_ctx.read(key)
                if b is None:
                    continue
                k = key.split("?")[1][len("key="):]
                out[k] = json.loads(b.decode("utf-8"))
            return out

    @ctx.http_method(ctx.method_post, "/file/{path:path}")
    async def write(self,
                    path: str = fastapi.Path(default=None),
                    data: Dict[str, Any] = fastapi.Body(default=None),
                    ):
        with self.db.context() as db_ctx:
            for key, val in data.items():
                db_ctx.write(f"{path}?key={key}", json.dumps(val).encode("utf-8"))
        self.file.flush()

    @ctx.http_method(ctx.method_delete, "/file/{path:path}")
    async def remove(self,
                     path: str = fastapi.Path(default=None),
                     ):
        with self.db.context() as db_ctx:
            for key in db_ctx.keys():
                if key.split("?")[0] == path:
                    db_ctx.delete(key)
        self.file.flush()
