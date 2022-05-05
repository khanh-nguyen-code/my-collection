from __future__ import annotations

from typing import Callable, Optional, Awaitable, Any

import pydantic

NodeId = int
Value = str

CODE_OK = 0
CODE_IGNORE = 1


class ProposalId(pydantic.BaseModel):
    id: int
    node_id: NodeId

    def __le__(self, other: ProposalId) -> bool:
        if self.id < other.id:
            return True
        if self.id == other.id and self.node_id <= other.node_id:
            return True
        return False

    def __lt__(self, other: ProposalId) -> bool:
        if self.id < other.id:
            return True
        if self.id == other.id and self.node_id < other.node_id:
            return True
        return False


class Proposal(pydantic.BaseModel):
    id: ProposalId
    value: Value

    def __hash__(self):
        return hash(str(self.id.node_id) + str(self.id.id) + str(self.value))


class Request(pydantic.BaseModel):
    pass


class PrepareRequest(Request):
    proposal_id: ProposalId


class ProposeRequest(Request):
    proposal: Proposal


class LogRequest(Request):
    sender: NodeId
    proposal: Proposal


class Response(pydantic.BaseModel):
    code: int = 0
    msg: Optional[str] = ""


class PrepareResponse(Response):
    proposal: Optional[Proposal] = None


class ProposeResponse(Response):
    proposal: Optional[Proposal] = None


def is_majority(num_nodes: int, num_responses: int) -> bool:
    return num_responses > num_nodes // 2


Unmarshaller = Callable[[Any], Response]

Router = Callable[[int, Request, Optional[Unmarshaller]], Awaitable[Optional[Response]]]
