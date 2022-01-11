from __future__ import annotations
from typing import Callable, Optional, Awaitable, TypeVar, Type, Any

import pydantic

NodeId = int
Value = str


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
        if self.id == other.id and self.node_id < other.id:
            return True
        return False


class Proposal(pydantic.BaseModel):
    id: ProposalId
    value: Value


class Message(pydantic.BaseModel):
    pass


class PrepareRequest(Message):
    proposal_id: ProposalId


class PrepareResponse(Message):
    proposal: Optional[Proposal]


class ProposeRequest(Message):
    proposal: Proposal


class ProposeResponse(Message):
    proposal: Proposal


class LogRequest(Message):
    sender: NodeId
    proposal: Proposal


def is_majority(num_nodes: int, num_responses: int) -> bool:
    return num_responses > num_nodes // 2


Unmarshaller = Callable[[Any], Message]

Router = Callable[[int, Message, Optional[Unmarshaller]], Awaitable[Optional[Message]]]
