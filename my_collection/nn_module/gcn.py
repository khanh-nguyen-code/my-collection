import numpy as np
import torch

from .module import Module


class GCN(Module):
    """
    GCN :
    """

    def __init__(self, sadj: torch.Tensor):
        """
        :param sadj: (n, n) scaled adjacency matrix
        """
        super(GCN, self).__init__()
        self.K = 2
        self.n = sadj.shape[0]
        self.sadj = sadj

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        :param x: (n, d) input signal where b is batch size, n is number of nodes, d is input dimension
        :return: (n, d) filtered signal.
        y = \Tidle{A} x where x \in \mathbb{R}^{n \times d}
        y \in mathbb{R}^{n \times d}
        """
        return self.sadj @ x

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(K={self.K}, n={self.n})"

    @staticmethod
    def prepare_sadj(adj: np.ndarray, directed: bool = False) -> np.ndarray:
        """
        :param adj: (n, n) adjacency matrix
        :param directed: whether the graph is directed
        :return: scaled adjacency matrix

        \hat{A} = A + I
        \hat{D} = diag(\hat{d}) where \hat{d}_i = \sum_{j=1}^n \hat{A}_{i j} % \hat{d}_i is the sum of row i of \hat{A}

        \Tidle{A} =
        \begin{cases}
            \hat{D}^{-\frac{1}{2}} \hat{A} \hat{D}^{-\frac{1}{2}} &\text{undirected} \\
            \hat{D}^{-1} \hat{A} &\text{directed}
        \end{cases}
        """
        n = adj.shape[0]
        adj_h = adj + np.identity(n=n)
        deg_h_vec = adj_h.sum(axis=0)
        if not directed:
            deg_h_m12 = np.zeros(shape=(n, n), dtype=np.float32)
            for i in range(n):
                if deg_h_vec[i] > 0:
                    deg_h_m12[i, i] = deg_h_vec[i] ** (-0.5)
            adj_n = deg_h_m12 @ adj_h @ deg_h_m12
            return adj_n.astype(np.float32)
        else:
            deg_m1 = np.zeros(shape=(n, n), dtype=np.float32)
            for i in range(n):
                if deg_h_vec[i] > 0:
                    deg_m1[i, i] = deg_h_vec[i] ** (-1.0)
            adj_n = deg_m1 @ adj_h
            return adj_n.astype(np.float32)
