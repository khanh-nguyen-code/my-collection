from typing import Dict

import requests

import logger
from codec import Codec


class Client:
    l: logger.Logger
    method: str
    path: str
    headers: Dict[str, str]
    content_type: str
    codec_map: Dict[str, Codec]

    def __init__(self, method: str, path: str, headers: Dict[str, str], content_type: str, codec_map: Dict[str, Codec]):
        self.l = logger.Logger()
        self.method = method
        self.path = path
        self.headers = headers
        self.content_type = content_type
        self.codec_map = codec_map
        self.headers["Content-Type"] = self.content_type

    def __call__(self, **kwargs):
        req_bytes = self.codec_map[self.content_type].marshal(kwargs)
        request = requests.Request(
            method=self.method,
            url=self.path,
            headers=self.headers,
            params=kwargs,
            data=req_bytes,
        )
        response = requests.Session().send(request.prepare())
        res_byte = response.content
        if response.status_code != 200:
            self.l.now(). \
                with_field("status_code", response.status_code). \
                with_field("body", res_byte.decode("utf-8")). \
                error("status code is not 200")
            return None
        content_type = response.headers["Content-Type"]
        res = self.codec_map[content_type].unmarshal(res_byte)
        return res


if __name__ == "__main__":
    pass
