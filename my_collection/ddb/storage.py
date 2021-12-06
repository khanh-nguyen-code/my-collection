from __future__ import annotations

import base64
import json
from functools import reduce
from typing import Any, Dict, Tuple

import dill
import fastapi
import plyvel
import pydantic

from my_collection import http
from my_collection.transform import t_map, t_filter


class TransformRequest(pydantic.BaseModel):
    transform_func: str  # base64 of transform.Transform
    reduce_func: str  # base64 of Callable[[Any, Any], Any]
    reduce_init: Any


ctx = http.Context()


class Storage(http.Server):
    def __init__(self, db_path: str, *args, **kwargs):
        super(Storage, self).__init__(ctx)
        self.db = plyvel.DB(db_path, create_if_missing=True, *args, **kwargs)

    @ctx.http_method(ctx.method_get, "/query/{path:path}")
    async def get(self,
                  path: str = fastapi.Path(default=None),
                  key: str = fastapi.Query(default=None),
                  ):
        out = self.db.get(f"{path}?key={key}".encode("utf-8"))
        if out is None:
            return None
        return json.loads(out)

    @ctx.http_method(ctx.method_post, "/query/{path:path}")
    async def post(self,
                   path: str = fastapi.Path(default=None),
                   key: str = fastapi.Query(default=None),
                   val: Any = fastapi.Body(default=None),
                   ):
        self.db.put(f"{path}?key={key}".encode("utf-8"), json.dumps(val).encode("utf-8"))

    @ctx.http_method(ctx.method_delete, "/query/{path:path}")
    async def delete(self,
                     path: str = fastapi.Path(default=None),
                     key: str = fastapi.Query(default=None),
                     ):
        self.db.delete(f"{path}?key={key}".encode("utf-8"))

    @ctx.http_method(ctx.method_post, "/transform/{path:path}")
    async def transform(self,
                        path: str = fastapi.Path(default=None),
                        t: TransformRequest = fastapi.Body(default=None),
                        ):
        transform_func = dill.loads(base64.b64decode(t.transform_func))
        reduce_func = dill.loads(base64.b64decode(t.reduce_func))

        sn = self.db.prefixed_db(f"{path}?key=".encode("utf-8")).snapshot()

        @t_map
        def kv_to_val(kv: Tuple[bytes, bytes]) -> Any:
            return json.loads(kv[1])

        func = transform_func * kv_to_val
        out = reduce(reduce_func, func(sn.iterator()), t.reduce_init)
        return out

    @ctx.http_method(ctx.method_get, "/file/{path:path}")
    async def read(self,
                   path: str = fastapi.Path(default=None),
                   ):
        sn = self.db.prefixed_db(f"{path}?key=".encode("utf-8")).snapshot()

        @t_map
        def kv_to_keyval(kv: Tuple[bytes, bytes]) -> Tuple[str, Any]:
            return kv[0].decode("utf-8").split("?")[1][len("key="):], json.loads(kv[1])

        return {key: val for key, val in kv_to_keyval(sn.iterator())}

    @ctx.http_method(ctx.method_post, "/file/{path:path}")
    async def write(self,
                    path: str = fastapi.Path(default=None),
                    data: Dict[str, Any] = fastapi.Body(default=None),
                    ):

        wb = self.db.write_batch()
        for key, val in data.items():
            wb.put(f"{path}?key={key}".encode("utf-8"), json.dumps(val).encode("utf-8"))

        wb.write()

    @ctx.http_method(ctx.method_delete, "/file/{path:path}")
    async def remove(self,
                     path: str = fastapi.Path(default=None),
                     ):
        db = self.db.prefixed_db(f"{path}?key=".encode("utf-8"))
        sn = db.snapshot()

        @t_map
        def kv_to_key(kv: Tuple[bytes, bytes]) -> str:
            return kv[0].decode("utf-8")

        wb = db.write_batch()
        for key, val in kv_to_key(sn.iterator()):
            if key.split("?")[0] == path:
                wb.delete(key)
        wb.write()
