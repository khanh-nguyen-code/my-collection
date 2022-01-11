from typing import Optional

from my_collection.paxos.common import NodeId, Value, Proposal, LogRequest, is_majority


class Learner:
    node_id: NodeId
    num_acceptors: int
    received: Optional[dict[Proposal, set[NodeId]]]
    committed: Optional[Value]

    def __init__(self, node_id: NodeId, num_acceptors: int):
        self.node_id = node_id
        self.num_acceptors = num_acceptors
        self.received = {}
        self.committed = None

    async def handle_log_request(self, request: LogRequest):
        if self.committed is not None:
            return
        if request.proposal.value not in self.received:
            self.received[request.proposal] = set()
        self.received[request.proposal].add(request.sender)
        if not is_majority(self.num_acceptors, len(self.received[request.proposal])):
            return
        self.committed = request.proposal.value
        self.received = None
