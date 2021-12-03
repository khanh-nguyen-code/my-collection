from typing import List

import numpy as np
from torch import nn


def dim(model: nn.Module) -> int:
    """
    :param model: torch module
    :return: dimension of trainable parameters
    """
    return sum(p.numel() for p in model.parameters())


def mat_stack(mat: List[List[np.ndarray]]) -> np.ndarray:
    """
    stack matrices
    example:

A = mat_stack([
    np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]]),
    np.array([[9, 10], [11, 12]]), np.array([[13, 14], [15, 16]]),
])
B = np.array([
    [ 1,  2,  3,  4],
    [ 5,  6,  7,  8],
    [ 9, 10, 11, 12],
    [13, 14, 15, 16],
])
assert np.linalg.norm(A - B) == 0

    Args:
        mat: np.ndarray

    Returns: np.ndarray
    """

    return np.vstack([np.hstack(row) for row in mat])
