import threading
from typing import Optional

import fastapi
import aiohttp
import uvicorn as uvicorn

from my_collection import http
from my_collection.paxos.acceptor import Acceptor
from my_collection.paxos.common import LogRequest, PrepareRequest, PrepareResponse, ProposeResponse, ProposeRequest, \
    Value, NodeId, Message, Unmarshaller, ProposalId
from my_collection.paxos.learner import Learner
from my_collection.paxos.proposer import Proposer

router = http.Router()


class Node(http.Server):
    proposer: Proposer
    acceptor: Acceptor
    learner: Learner
    addr_list: list[str]

    def __init__(self, node_id: NodeId, addr_list: list[str]):
        super().__init__(router)
        self.addr_list = addr_list
        self.proposer = Proposer(node_id, list(range(len(addr_list))), self.route)
        self.acceptor = Acceptor(node_id, list(range(len(addr_list))), self.route)
        self.learner = Learner(node_id, len(addr_list))

    async def route(self, node_id: NodeId, request: Message, unmarshaller: Unmarshaller) -> Optional[Message]:
        path = self.addr_list[node_id]
        if isinstance(request, PrepareRequest):
            path += "/internal/prepare"
        if isinstance(request, ProposeRequest):
            path += "/internal/propose"
        if isinstance(request, LogRequest):
            path += "/internal/log"

        async with aiohttp.ClientSession() as session:
            async with session.post(path, data=request.dict()) as r:
                if r.status != 200:
                    return None
                if unmarshaller is None:
                    return None
                o = await r.json()
                if o is None:
                    return None
                response = unmarshaller(o)
                return response

    @router.http_method(router.method_post, "/internal/log")
    async def internal_log(self, body: LogRequest = fastapi.Body(default=None)) -> None:
        return await self.learner.handle_log_request(body)

    @router.http_method(router.method_post, "/internal/prepare")
    async def internal_prepare(self, body: PrepareRequest = fastapi.Body(default=None)) -> Optional[PrepareResponse]:
        return await self.acceptor.handle_prepare_request(body)

    @router.http_method(router.method_post, "/internal/propose")
    async def internal_propose(self, body: ProposeRequest = fastapi.Body(default=None)) -> Optional[ProposeResponse]:
        return await self.acceptor.handle_propose_request(body)

    @router.http_method(router.method_post, "/propose")
    async def propose(self, value: Value = fastapi.Query(default=None)) -> Optional[Value]:
        return await self.proposer.propose_once(value)

    @router.http_method(router.method_get, "/committed")
    async def committed(self) -> Value:
        return self.learner.committed


if __name__ == "__main__":
    addr_list = []
    port_list = []
    n = 3
    for i in range(n):
        port_list.append(3000 + i)
        addr_list.append(f"http://localhost:{3000 + i}")

    node_list = []
    for i in range(n):
        node_list.append(Node(i, addr_list))

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