from __future__ import annotations

import base64
import os
from functools import reduce
from typing import Any

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

    @ctx.http_method(ctx.method_get, "/data/{path:path}")
    def get(self,
            path: str = fastapi.Path(default=None),
            key: str = fastapi.Query(default=None),
            ):
        with self.db.context() as db_ctx:
            return db_ctx.read(f"{path}?key={key}").decode("utf-8")

    @ctx.http_method(ctx.method_post, "/data/{path:path}")
    def post(self,
             path: str = fastapi.Path(default=None),
             key: str = fastapi.Query(default=None),
             val: str = fastapi.Body(default=None),
             ):
        with self.db.context() as db_ctx:
            db_ctx.write(f"{path}?key={key}", val.encode("utf-8"))
            self.file.flush()

    @ctx.http_method(ctx.method_delete, "/data/{path:path}")
    def delete(self,
               path: str = fastapi.Path(default=None),
               key: str = fastapi.Query(default=None),
               ):
        with self.db.context() as db_ctx:
            db_ctx.delete(f"{path}?key={key}")
            self.file.flush()

    @ctx.http_method(ctx.method_post, "/transform/{path:path}")
    def transform(self,
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
            def key_to_val(key: str) -> str:
                return db_ctx.read(key).decode("utf-8")

            func = transform_func * key_to_val * key_filter
            out = reduce(reduce_func, func(db_ctx.keys()), t.reduce_init)
            print(db_ctx.keys(), out)
            return out
