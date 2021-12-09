from typing import List, Optional

import torch
from .module import Module
from torch import nn


class WeightedPool1D(Module):
    """
    WeightedPool1D :
    """

    def __init__(self, clustering: Optional[List[List[int]]] = None):
        """
        :param clustering: K lists, each list contains its nodes
        """
        super(WeightedPool1D, self).__init__()
        self.clustering = clustering
        self.out_dim = len(clustering)
        self.in_dim = sum(len(e) for e in clustering)
        self.weight = nn.Parameter(torch.empty(size=(self.out_dim, self.in_dim), dtype=torch.float32))
        self.reset_parameters()
        # set mask
        self.mask = torch.zeros(size=(self.out_dim, self.in_dim), dtype=torch.float32)
        for c in range(len(clustering)):
            for n in clustering[c]:
                self.mask[c, n] = 1.0

    def reset_parameters(self):
        self.weight.data.uniform_(-1 / self.in_dim, +1 / self.in_dim)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.in_dim} -> {self.out_dim})"

    def forward(self, x_batch: torch.Tensor) -> torch.Tensor:
        """
        :param x_batch: (b, n, d) input signal where b is batch size, n is number of nodes, d is input dimension
        :return: (b, K, d) filtered signal.
        y_b_k =  \sum_{i \in C_k} w_i x_{b i}
        """
        return torch.stack([(self.mask * self.weight) @ x for x in x_batch])
