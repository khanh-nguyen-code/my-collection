import base64
from typing import Any, Callable, Dict

import dill
import fastapi
import requests

from my_collection import transform
from my_collection.ddb.server import Addr
from my_collection.ddb.storage import TransformRequest


class Client:
    def __init__(self, addr: Addr):
        self.addr = addr

    def get(self, path: str, key: str) -> Any:
        r = requests.get(f"http://{self.addr.host}:{self.addr.port}/query/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    def post(self, path: str, key: str, val: Any):
        r = requests.post(f"http://{self.addr.host}:{self.addr.port}/query/{path}?key={key}", json=val)
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)

    def delete(self, path: str, key: str):
        r = requests.delete(f"http://{self.addr.host}:{self.addr.port}/query/{path}?key={key}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)

    def transform(self, path: str, transform_func: transform.Transform, reduce_func: Callable[[Any, Any], Any]) -> Any:
        t = TransformRequest(
            transform_func=base64.b64encode(dill.dumps(transform_func)),
            reduce_func=base64.b64encode(dill.dumps(reduce_func)),
            reduce_init=0,
        )
        r = requests.post(f"http://{self.addr.host}:{self.addr.port}/transform/{path}", json=t.dict())
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    def read(self, path: str) -> Dict[str, Any]:
        r = requests.get(f"http://{self.addr.host}:{self.addr.port}/file/{path}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

    def write(self, path: str, data: Dict[str, Any]):
        r = requests.post(f"http://{self.addr.host}:{self.addr.port}/file/{path}", json=data)
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)

    def remove(self, path: str):
        r = requests.delete(f"http://{self.addr.host}:{self.addr.port}/file/{path}")
        if r.status_code != 200:
            raise fastapi.HTTPException(status_code=r.status_code, detail=r.text)
