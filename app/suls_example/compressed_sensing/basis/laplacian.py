from typing import Optional, Tuple

import numpy as np
import scipy as sp
import scipy.sparse
import scipy.sparse.linalg


def basis(adj: sp.sparse.spmatrix, d: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
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
    w = w.astype(np.float64)
    return w.T, w


def create_grid_adj_matrix(grid_h: int, grid_w: int) -> sp.sparse.coo_matrix:
    """
    :return: adjacency of the grid graph
    """
    coord_list = []
    for h in range(grid_h):
        for w in range(grid_w):
            coord_list.append((h, w))
    n = len(coord_list)

    c2i = {coord: i for i, coord in enumerate(coord_list)}

    def is_inside(h: int, w: int) -> bool:
        if h < 0 or h >= grid_h or w < 0 or w >= grid_h:
            return False
        return True

    adj = np.zeros(shape=(n, n), dtype=bool)
    for h0, w0 in coord_list:
        for dh, dw in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            h1, w1 = h0 + dh, w0 + dw
            if is_inside(h1, w1):
                i0, i1 = c2i[(h0, w0)], c2i[(h1, w1)]
                adj[i0, i1] = True
    adj = sp.sparse.coo_matrix(adj)
    return adj
