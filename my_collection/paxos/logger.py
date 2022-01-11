import asyncio
import json
import threading
from collections import namedtuple
from typing import Optional

import aiohttp
import fastapi
import uvicorn

from my_collection import http
from my_collection.paxos.acceptor import Acceptor
from my_collection.paxos.common import LogRequest, PrepareRequest, PrepareResponse, ProposeResponse, ProposeRequest, NodeId, Request, Unmarshaller, Response, CODE_OK
from my_collection.paxos.learner import Learner
from my_collection.paxos.proposer import Proposer

router = http.Router()

Version = namedtuple("Version", ["proposer", "acceptor", "learner"])


class Logger(http.Server):
    node_id: NodeId
    addr_list: list[str]
    log: list[Version]
    line: int

    def __init__(self, node_id: NodeId, addr_list: list[str]):
        super().__init__(router)
        self.node_id = node_id
        self.addr_list = addr_list
        self.log = []
        self.line = 0

    def extend_log(self):
        log_id = len(self.log)
        self.log.append(Version(
            proposer=Proposer(self.node_id, list(range(len(addr_list))), self.route(log_id)),
            acceptor=Acceptor(self.node_id, list(range(len(addr_list))), self.route(log_id)),
            learner=Learner(self.node_id, len(addr_list)),
        ))

    def route(self, log_id: int):
        async def helper(node_id: NodeId, request: Request, unmarshaller: Unmarshaller) -> Optional[Response]:
            path = self.addr_list[node_id]
            if isinstance(request, PrepareRequest):
                path += "/internal/prepare"
            if isinstance(request, ProposeRequest):
                path += "/internal/propose"
            if isinstance(request, LogRequest):
                path += "/internal/log"
            path += f"/{log_id}"
            async with aiohttp.ClientSession() as session:
                async with session.post(path, json=request.dict()) as r:
                    if r.status != 200:
                        return None
                    o = await r.json()
                    if o is None:
                        return None
                    if unmarshaller is None:
                        return None
                    response = unmarshaller(o)
                    if response.code != CODE_OK:
                        print(response)
                    return response

        return helper

    @router.http_method(router.method_post, "/internal/log/{log_id}")
    async def internal_log(self, log_id: int = fastapi.Path(default=None),
                           body: LogRequest = fastapi.Body(default=None)) -> None:
        while log_id >= len(self.log):
            self.extend_log()
        return await self.log[log_id].learner.handle_log_request(body)

    @router.http_method(router.method_post, "/internal/prepare/{log_id}")
    async def internal_prepare(self, log_id: int = fastapi.Path(default=None),
                               body: PrepareRequest = fastapi.Body(default=None)) -> Optional[PrepareResponse]:
        while log_id >= len(self.log):
            self.extend_log()
        return await self.log[log_id].acceptor.handle_prepare_request(body)

    @router.http_method(router.method_post, "/internal/propose/{log_id}")
    async def internal_propose(self, log_id: int = fastapi.Path(default=None),
                               body: ProposeRequest = fastapi.Body(default=None)) -> Optional[ProposeResponse]:
        while log_id >= len(self.log):
            self.extend_log()
        return await self.log[log_id].acceptor.handle_propose_request(body)

    @router.http_method(router.method_post, "/propose")
    async def propose(self, inValue: str = fastapi.Query(default=None)) -> list[str]:
        value = json.dumps({
            "node_id": self.node_id,
            "line": self.line,
            "value": inValue},
        )
        while True:
            self.extend_log()
            log_id = len(self.log) - 1
            if self.log[log_id].learner.committed is None:
                wait = 0.15  # s
                max_wait = 2  # s
                while True:
                    if self.log[log_id].learner.committed is not None:
                        break
                    value = await self.log[log_id].proposer.propose_once(value)
                    if value is not None:
                        self.log[log_id].learner.committed = value
                        self.log[log_id].learner.received = None
                        break
                    if self.log[log_id].learner.committed is not None:
                        break
                    await asyncio.sleep(wait)
                    wait *= 2
                    if wait > max_wait:
                        wait = max_wait
            if self.log[log_id].learner.committed == value:
                break
        self.line += 1
        return [log.learner.committed for log in self.log]

    @router.http_method(router.method_get, "/read")
    async def read(self) -> list[str]:
        return [log.learner.committed for log in self.log]


if __name__ == "__main__":
    addr_list = []
    port_list = []
    n = 3
    for i in range(n):
        port_list.append(3000 + i)
        addr_list.append(f"http://localhost:{3000 + i}")

    node_list = []
    for i in range(n):
        node_list.append(Logger(i, addr_list))

    thread_list = []
    for i in range(n):
        thread_list.append(threading.Thread(target=uvicorn.run, args=(node_list[i].app,), kwargs={
            "host": "localhost",
            "port": port_list[i],
            "loop": "asyncio",
        }))
        thread_list[-1].start()
    for thread in thread_list:
        thread.join()
