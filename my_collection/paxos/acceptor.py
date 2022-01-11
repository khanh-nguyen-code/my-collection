from typing import Optional, Callable

from my_collection.paxos.common import NodeId, ProposalId, Proposal, PrepareRequest, PrepareResponse, ProposeRequest, \
    LogRequest, Message, ProposeResponse, Router


class Acceptor:
    node_id: NodeId
    learner_id_list: list[NodeId]
    router: Router
    promised: ProposalId  # init {0, -1}
    accepted: Optional[Proposal]

    def __init__(self, node_id: NodeId, learner_id_list: list[NodeId], router: Router):
        self.node_id = node_id
        self.learner_id_list = learner_id_list
        self.router = router
        self.promised = ProposalId(id=0, node_id=-1)
        self.accepted = None

    async def handle_prepare_request(self, request: PrepareRequest) -> Optional[PrepareResponse]:
        if request.proposal_id <= self.promised:
            return None
        self.promised = request.proposal_id
        return PrepareResponse(proposal=self.accepted)

    async def handle_propose_request(self, request: ProposeRequest) -> Optional[ProposeResponse]:
        if request.proposal.id < self.promised:
            return None
        self.accepted = request.proposal
        log_request = LogRequest(sender=self.node_id, proposal=self.accepted)
        for learner_id in self.learner_id_list:
            await self.router(learner_id, log_request, None)
        response = ProposeResponse(proposal=self.accepted)
        return response
