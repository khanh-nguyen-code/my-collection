import numpy as np
import scipy as sp
import scipy.sparse
import torch

def from_scipy(mx: sp.sparse.spmatrix) -> torch.Tensor:
    """
    :param mx: (n, n) scipy sparse matrix
    :return: (n, n) torch sparse tensor
    """
    mx = mx.tocoo()
    if len(mx.row) == 0 and len(mx.col) == 0:
        indices = torch.LongTensor([[], []])
    else:
        indices = torch.from_numpy(
            np.vstack((mx.row, mx.col)).astype(np.int64),
        )
    values = torch.from_numpy(mx.data)  # preserve type
    shape = torch.Size(mx.shape)
    return torch.sparse_coo_tensor(indices, values, shape)
