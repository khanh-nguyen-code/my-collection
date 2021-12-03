from typing import Tuple

import numpy as np


def forward(h1_d: int, w1_d: int, h2_d: int, w2_d: int) -> np.ndarray:
    """
    forward
    :param h1_d: vertical spatial dimension
    :param w1_d: horizontal spatial dimension
    :param h2_d: vertical spectral dimension
    :param w2_d: horizontal spectral dimension
    :return: transform matrix (row-major)
    """
    M = np.empty(shape=(h2_d * w2_d, h1_d * w1_d), dtype=np.complex128)
    for h2 in range(h2_d):
        for w2 in range(w2_d):
            i2 = h2 * w2_d + w2  # row major
            for h1 in range(h1_d):
                for w1 in range(w1_d):
                    i1 = h1 * w1_d + w1  # row major
                    M[i2, i1] = complex(0, - 2 * np.pi * (h2 * h1 / h1_d + w2 * w1 / w1_d))
    return np.exp(M) / (h1_d * w1_d)


def backward(h2_d: int, w2_d: int, h1_d: int, w1_d: int) -> np.ndarray:
    """
    backward
    :param h1_d: vertical spatial dimension
    :param w1_d: horizontal spatial dimension
    :param h2_d: vertical spectral dimension
    :param w2_d: horizontal spectral dimension
    :return: transform matrix (row-major)
    """
    M = np.empty(shape=(h1_d * w1_d, h2_d * w2_d), dtype=np.complex128)
    for h1 in range(h1_d):
        for w1 in range(w1_d):
            i1 = h1 * w1_d + w1  # row major
            for h2 in range(h2_d):
                for w2 in range(w2_d):
                    i2 = h2 * w2_d + w2  # row major
                    M[i1, i2] = complex(0, 2 * np.pi * (h2 * h1 / h1_d + w2 * w1 / w1_d))
    return np.exp(M)


def basis(h1_d: int, w1_d: int, h2_d: int, w2_d: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    :param h1_d: vertical spatial dimension
    :param w1_d: horizontal spatial dimension
    :param h2_d: vertical spectral dimension
    :param w2_d: horizontal spectral dimension
    """
    return forward(h1_d, w1_d, h2_d, w2_d), backward(h2_d, w2_d, h1_d, w1_d)
