import base64
from functools import reduce
from typing import List

import dill
import fastapi
import pydantic
import requests

from my_collection import http, logger
from my_collection.ddb.storage import TransformRequest


class Addr(pydantic.BaseModel):
    host: str
    port: int


ctx = http.Context()


class Server(http.Server):
    def __init__(self, storage_list: List[Addr]):
        super().__init__(ctx)
        self.storage_list = storage_list

    @ctx.http_method(ctx.method_get, "/data/{path:path}")
    def get(self,
            path: str = fastapi.Path(default=None),
            key: str = fastapi.Query(default=None),
            ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.get(f"http://{addr.host}:{addr.port}/data/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    @ctx.http_method(ctx.method_post, "/data/{path:path}")
    def post(self,
             path: str = fastapi.Path(default=None),
             key: str = fastapi.Query(default=None),
             val: str = fastapi.Body(default=None),
             ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.post(f"http://{addr.host}:{addr.port}/data/{path}?key={key}", json=val)
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        logger.now().debug(f"write {path}?key={key} into storage {storage_idx}")

    @ctx.http_method(ctx.method_delete, "/data/{path:path}")
    def delete(self,
               path: str = fastapi.Path(default=None),
               key: str = fastapi.Query(default=None),
               ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.delete(f"http://{addr.host}:{addr.port}/data/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        logger.now().debug(f"write {path}?key={key} from storage {storage_idx}")

    @ctx.http_method(ctx.method_post, "/transform/{path:path}")
    def transform(self,
                  path: str = fastapi.Path(default=None),
                  t: TransformRequest = fastapi.Body(default=None),
                  ):
        out = []
        for addr in self.storage_list:
            r = requests.post(f"http://{addr.host}:{addr.port}/transform/{path}", json=t.dict())
            if r.status_code != 200:
                raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
            out.append(r.json())
        reduce_func = dill.loads(base64.b64decode(t.reduce_func))
        return reduce(reduce_func, out)
