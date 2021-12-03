import base64
from functools import reduce
from typing import List, Dict, Any

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

    @ctx.http_method(ctx.method_get, "/query/{path:path}")
    async def get(self,
                  path: str = fastapi.Path(default=None),
                  key: str = fastapi.Query(default=None),
                  ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.get(f"http://{addr.host}:{addr.port}/query/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    @ctx.http_method(ctx.method_post, "/query/{path:path}")
    async def post(self,
                   path: str = fastapi.Path(default=None),
                   key: str = fastapi.Query(default=None),
                   val: Any = fastapi.Body(default=None),
                   ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.post(f"http://{addr.host}:{addr.port}/query/{path}?key={key}", json=val)
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        logger.now().debug(f"write {path}?key={key} into storage {storage_idx}")

    @ctx.http_method(ctx.method_delete, "/query/{path:path}")
    async def delete(self,
                     path: str = fastapi.Path(default=None),
                     key: str = fastapi.Query(default=None),
                     ):
        storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
        addr = self.storage_list[storage_idx]
        r = requests.delete(f"http://{addr.host}:{addr.port}/query/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        logger.now().debug(f"write {path}?key={key} from storage {storage_idx}")

    @ctx.http_method(ctx.method_post, "/transform/{path:path}")
    async def transform(self,
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

    @ctx.http_method(ctx.method_get, "/file/{path:path}")
    async def read(self,
                   path: str = fastapi.Path(default=None),
                   ):
        out = {}
        for addr in self.storage_list:
            r = requests.get(f"http://{addr.host}:{addr.port}/file/{path}")
            if r.status_code != 200:
                continue
            out = out | r.json()
        return out

    @ctx.http_method(ctx.method_post, "/file/{path:path}")
    async def write(self,
                    path: str = fastapi.Path(default=None),
                    data: Dict[str, Any] = fastapi.Body(default=None),
                    ):
        data_list = [{} for _ in self.storage_list]

        for key, val in data.items():
            storage_idx = hash(f"{path}?key={key}") % len(self.storage_list)
            data_list[storage_idx][key] = val

        for i, addr in enumerate(self.storage_list):
            requests.post(f"http://{addr.host}:{addr.port}/file/{path}", json=data_list[i])

    @ctx.http_method(ctx.method_delete, "/file/{path:path}")
    async def remove(self,
                     path: str = fastapi.Path(default=None),
                     ):
        for addr in self.storage_list:
            requests.delete(f"http://{addr.host}:{addr.port}/file/{path}")
