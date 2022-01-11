from typing import Optional

from my_collection.paxos.common import NodeId, Router, ProposalId, Value, PrepareRequest, is_majority, PrepareResponse, \
    Proposal, LogRequest, ProposeRequest, ProposeResponse, CODE_OK


class Proposer:
    node_id: NodeId
    acceptor_id_list: list[NodeId]
    router: Router
    current_proposal_id: ProposalId  # init {0, node_id}

    def __init__(self, node_id: NodeId, acceptor_id_list: list[NodeId], router: Router):
        self.node_id = node_id
        self.acceptor_id_list = acceptor_id_list
        self.router = router
        self.current_proposal_id = ProposalId(id=0, node_id=node_id)

    async def propose_once(self, value: Value) -> Optional[Value]:
        proposal_id = self.current_proposal_id
        self.current_proposal_id.id += 1

        request = PrepareRequest(proposal_id=proposal_id)
        response_list: list[PrepareResponse] = [
            await self.router(acceptor_id, request, PrepareResponse.parse_obj)
            for acceptor_id in self.acceptor_id_list
        ]
        response_list: list[PrepareResponse] = [
            response
            for response in response_list
            if response is not None and response.code == CODE_OK
        ]
        if not is_majority(len(self.acceptor_id_list), len(response_list)):
            return None
        accepted_proposal_list = [
            response.proposal
            for response in response_list
            if response.proposal is not None
        ]
        if len(accepted_proposal_list) > 0:
            proposal = max(accepted_proposal_list, key=lambda x: x.id)
        else:
            proposal = Proposal(id=proposal_id, value=value)

        request = ProposeRequest(proposal=proposal)
        response_list: list[ProposeResponse] = [
            await self.router(acceptor_id, request, ProposeResponse.parse_obj)
            for acceptor_id in self.acceptor_id_list
        ]
        response_list: list[ProposeResponse] = [
            response
            for response in response_list
            if response is not None and response.code == CODE_OK
        ]

        if not is_majority(len(self.acceptor_id_list), len(response_list)):
            return None
        return response_list[0].proposal.value
