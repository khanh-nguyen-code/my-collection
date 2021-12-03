import math
from typing import Optional

import numpy as np
import scipy as sp
import scipy.sparse
import scipy.sparse.linalg
import torch
from torch import nn

from nn_module import Module


class GraphConv(Module):
    """
    GraphConv :
    """

    def __init__(self, u: torch.Tensor, c: int):
        """
        :param u: (n, d) basis
        :param c: number of channels
        """
        super(GraphConv, self).__init__()
        self.n = u.shape[0]
        self.d = u.shape[1]
        self.u = u
        self.c = c
        self.w = nn.Parameter(torch.empty((self.n, self.c), dtype=torch.float32))
        self.reset_parameters()
        # precompute u^T
        self.u_t = torch.transpose(u, 0, 1)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(n={self.n}, d={self.d}, c={self.c})"

    def reset_parameters(self):
        self.w.data.uniform_(-1 / math.sqrt(self.n), +1 / math.sqrt(self.n))

    def forward(self, x: torch.Tensor):
        """
        :param x: (n, c) input signal where b is batch size, n is number of nodes, c is number of channels
        :return: (n, c) filtered signal.
        y =  U ( U^T w \odot U^T x ) where x \in \mathbb{R}^{n \times d}
        y \in mathbb{R}^{n \times d}
        """
        return self.u @ ((self.u_t @ self.w) * (self.u_t @ x))

    @staticmethod
    def prepare_u(adj: sp.sparse.spmatrix, d: Optional[int] = None) -> np.ndarray:
        """
        :param adj: (n, n) adjacency matrix
        :param d: () dimension, default n
        :return: (n, d) graph laplacian basis
        """
        n = adj.shape[0]
        if d is None:
            d = n
        # normalized lap
        adj = adj.tocsr()
        adj = abs((adj + adj.T) / 2)  # make adj symmetric, return csr_matrix
        deg_vec = np.array(np.sum(adj, axis=0))[0]
        deg = sp.sparse.diags(deg_vec)
        lap = deg - adj
        if d < n:
            v, w = sp.sparse.linalg.eigsh(lap, k=d, which="SM")
        else:
            v, w = sp.linalg.eigh(lap.toarray())
        return w.astype(np.float32)
