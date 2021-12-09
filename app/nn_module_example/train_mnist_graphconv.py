from typing import Tuple, List

import cv2
import numpy as np
import scipy as sp
import scipy.sparse
import torch
from my_collection.nn_module import GraphConv
from my_collection.nn_module import Functional, Batch
from my_collection.nn_module import WeightedPool1D
from torch import nn

import mnist
import util

IMAGE_SIZE = 25
KERNEL_SIZE = 5

HDIM = 32
IDIM = 1
ODIM = 10


def square_grid(grid_size: int, kernel_size: int) -> Tuple[sp.sparse.coo_matrix, List[List[int]]]:
    """
    :param grid_size:
    :param kernel_size:
    :return: adjacency of the grid graph, clustering of that grid graph w.r.t kernel size
    """
    coord_list = []
    for h in range(grid_size):
        for w in range(grid_size):
            coord_list.append((h, w))
    n = len(coord_list)

    c2i = {coord: i for i, coord in enumerate(coord_list)}

    def is_inside(h: int, w: int) -> bool:
        if h < 0 or h >= grid_size or w < 0 or w >= grid_size:
            return False
        return True

    adj = np.zeros(shape=(n, n), dtype=np.bool)
    for h0, w0 in coord_list:
        for dh, dw in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            h1, w1 = h0 + dh, w0 + dw
            if is_inside(h1, w1):
                i0, i1 = c2i[(h0, w0)], c2i[(h1, w1)]
                adj[i0, i1] = True
    adj = sp.sparse.coo_matrix(adj, dtype=np.float32)
    c_list = []
    for tl_h in range(0, grid_size, kernel_size):
        for tl_w in range(0, grid_size, kernel_size):
            c = []
            for dh in range(kernel_size):
                for dw in range(kernel_size):
                    h, w = tl_h + dh, tl_w + dw
                    c.append(c2i[(h, w)])
            c_list.append(c)
    return adj, c_list


def create_model(hdim: int, image_size: int, kernel_size: int, K: int):
    """
    :param hdim: hidden dimension
    :param K: number vectors in chebyshev basis
    :param image_size: must equal kernel_size^n
    :param kernel_size: kernel size, image must be in the shape of (image_size^2)
    """
    # head
    head = [nn.Linear(IDIM, hdim), ]
    # body
    body = []
    image_size_in = image_size
    while True:
        image_size_out = image_size_in // kernel_size
        adj, c_list = square_grid(image_size_in, kernel_size)
        body.extend([
            Batch(GraphConv(u=torch.from_numpy(GraphConv.prepare_u(adj, hdim)), c=hdim)),
            nn.Dropout(),
            nn.ReLU(),
            nn.Linear(hdim, hdim),
            WeightedPool1D(c_list)
        ])
        if image_size_out == 1:  # last layer of ChebNet
            break
        image_size_in = image_size_out

    # tail
    tail = [
        Functional(lambda x: x[:, 0, :], name="(b, 1, d) -> (b, d)"),  # (b, 1, d) -> (b, d)
        nn.Linear(hdim, hdim),
        nn.Dropout(),
        nn.ReLU(),
        nn.Linear(hdim, ODIM),
    ]
    return nn.Sequential(*head, *body, *tail)


def preprocess(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    X_out = np.empty(shape=(X.shape[0], IMAGE_SIZE * IMAGE_SIZE), dtype=np.float32)
    for row, im in enumerate(X.reshape((-1, 28, 28))):
        X_out[row, :] = cv2.resize(im, dsize=(IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_LINEAR).flatten()
    return X_out.reshape((-1, IMAGE_SIZE * IMAGE_SIZE, 1)).astype(np.float32), y.astype(np.int64)


if __name__ == "__main__":
    model = create_model(hdim=32, image_size=IMAGE_SIZE, kernel_size=KERNEL_SIZE, K=2)
    print(model)
    print(util.dim(model))

    mnist.train(preprocess, model)
