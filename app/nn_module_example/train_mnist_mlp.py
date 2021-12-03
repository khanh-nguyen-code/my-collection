from typing import Tuple

import cv2
import numpy as np
from torch import nn

import mnist
import util

IMAGE_SIZE = 25
KERNEL_SIZE = 5

HDIM = 32
IDIM = 1
ODIM = 10


def create_model(hdim: int):
    """
    :param hdim: hidden dimension
    """
    return nn.Sequential(
        nn.Linear(in_features=IDIM * IMAGE_SIZE * IMAGE_SIZE, out_features=hdim),
        nn.Dropout(),
        nn.Sigmoid(),
        nn.Linear(in_features=hdim, out_features=ODIM),
    )


def preprocess(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    X_out = np.empty(shape=(X.shape[0], IMAGE_SIZE * IMAGE_SIZE), dtype=np.float32)
    for row, im in enumerate(X.reshape((-1, 28, 28))):
        X_out[row, :] = cv2.resize(im, dsize=(IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_LINEAR).flatten()
    return X_out.reshape((-1, IMAGE_SIZE * IMAGE_SIZE)).astype(np.float32), y.astype(np.int64)


if __name__ == "__main__":
    model = create_model(hdim=128)
    print(model)
    print(util.dim(model))

    mnist.train(preprocess, model)
