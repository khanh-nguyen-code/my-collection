from typing import List

import networkx as nx
import numpy as np
import torch
from my_collection.nn_module import GraphConv
from torch import nn, optim

g = nx.karate_club_graph()

n = g.number_of_nodes()
adj = nx.adjacency_matrix(g).astype(np.float32)

adj = (adj + adj.T) / 2  # make symmetric

label_str = [v for v in nx.get_node_attributes(g, "club").values()]
label_str_unique = list(set(label_str))
label = [label_str_unique.index(l) for l in label_str]


def accuracy(prediction: List[int]) -> float:
    total = 0
    correct = 0
    for pred, actual in zip(prediction, label):
        total += 1
        if pred == actual:
            correct += 1
    return correct / total


u = torch.from_numpy(GraphConv.prepare_u(adj, 5))
model = nn.Sequential(
    GraphConv(u, 8),
    nn.Linear(8, 8),
    nn.ReLU(),
    GraphConv(u, 8),
    nn.Linear(8, 2),
)

x = torch.randn(size=(n, 8), dtype=torch.float32)
target = torch.tensor(label, dtype=torch.int64)
optimizer = optim.SGD(model.parameters(), lr=1e-1)


def decode() -> List[int]:
    with torch.no_grad():
        logits = model.forward(x).detach().cpu().numpy()
        return list((logits[:, 0] < logits[:, 1]).astype(int))


for i in range(10000):
    model.train()
    model.zero_grad()
    output = model.forward(x)
    loss = nn.CrossEntropyLoss().forward(output, target)
    loss.backward()
    loss_v = float(loss.detach().cpu().numpy())
    model.eval()
    print(f"loss {loss_v}, accuracy {accuracy(decode())}")
    optimizer.step()

pass
