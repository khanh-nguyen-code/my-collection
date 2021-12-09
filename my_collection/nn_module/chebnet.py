import numpy as np
import scipy as sp
import scipy.sparse
import scipy.sparse.linalg
import torch
from .module import Module
from torch import nn


class ChebNet(Module):
    """
    ChebNet:
    """

    def __init__(self, k: int, slap: torch.Tensor, d: int):
        """
        :param k: () number of vectors in Chebyshev basis.
        :param slap: (n, n) scaled normalized laplacian matrix. (2L / lambda_max - I)
        :param d: () number of channels
        """
        super(ChebNet, self).__init__()
        self.K = k
        self.n = slap.shape[0]
        self.d = d
        self.slap = slap
        self.theta = nn.Parameter(torch.empty((self.K, 1, d), dtype=torch.float32))
        self.reset_parameters()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(K={self.K}, n={self.n}, d={self.d})"

    def reset_parameters(self):
        self.theta.data.uniform_(-1 / self.K, +1 / self.K)

    def forward(self, x: torch.Tensor):
        """
        :param x: (n, d) input signal where b is batch size, n is number of nodes, d is input dimension
        :return: (n, d) filtered signal.
        y = \sum_{k=0}^{K-1} \theta_k T_k(\Tilde{\Lambda}) x where x \in \mathbb{R}^{n \times d}
        y \in \mathbb{R}^{n \times d}
        """
        # Chebyshev basis
        # T_0(\Tilde{\Lambda}) = I
        # T_1(\Tilde{\Lambda}) = \Tilde{\Lambda}
        # T_k(\Tilde{\Lambda}) = 2 \Tilde{\Lambda} T_{k-1}(\Tilde{\Lambda}) - T_{k-2}(\Tilde{\Lambda})
        Tx = [x, torch.sparse.mm(self.slap, x)]
        for k in range(2, self.K):
            Tx_k = 2 * torch.sparse.mm(self.slap, Tx[k - 1]) - Tx[k - 2]
            Tx.append(Tx_k)
        Tx = torch.stack(Tx)
        wsum = (self.theta * Tx).sum(axis=0)
        return wsum

    @staticmethod
    def prepare_slap(adj: sp.sparse.spmatrix) -> sp.sparse.coo_matrix:
        """
        :param adj: (n, n) adjacency matrix
        :return: (n, n) scaled laplacian matrix used for ChebNet
        """
        adj = adj.tocsr()
        adj = abs((adj + adj.T) / 2)  # make adj symmetric, return csr_matrix
        # normalized lap
        n = adj.shape[0]
        deg_vec = np.array(np.sum(adj, axis=0))[0]
        deg = sp.sparse.diags(deg_vec)
        lap = deg - adj
        deg_m12_vec = np.zeros(shape=(n,), dtype=np.float32)
        for i in range(n):
            if deg_vec[i] > 0:
                deg_m12_vec[i] = deg_vec[i] ** (-0.5)
        deg_m12 = sp.sparse.diags(deg_m12_vec)
        nlap = deg_m12 @ lap @ deg_m12

        # scaled lap
        lambda_max = sp.sparse.linalg.eigsh(nlap, k=1, which="LM")[0][0]  # 0 <= lambda_max <= 2
        slap = 2 * nlap / lambda_max - sp.sparse.identity(n, dtype=np.float32)
        return slap.astype(np.float32).tocoo()
