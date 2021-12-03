from typing import Tuple

import cv2
import numpy as np
from torch import nn

import mnist
import util
from module.module import Functional

IMAGE_SIZE = 25
KERNEL_SIZE = 5

HDIM = 32
IDIM = 1
ODIM = 10


def create_model(hdim: int, image_size: int, kernel_size: int):
    assert kernel_size % 2 == 1
    pad = (kernel_size // 2, kernel_size // 2)
    # head
    head = [nn.Conv2d(in_channels=IDIM, out_channels=hdim, kernel_size=(1, 1))]
    # body
    body = []
    image_size_in = image_size
    while True:
        image_size_out = image_size_in // kernel_size
        body.extend([
            nn.Conv2d(in_channels=hdim, out_channels=hdim, kernel_size=(kernel_size, kernel_size), padding=pad),
            nn.Dropout(),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=kernel_size),
        ])
        if image_size_out == 1:  # last layer
            break
        image_size_in = image_size_out
    # tail
    tail = [
        Functional(lambda x: x.max(dim=-1)[0].max(dim=-1)[0], name="maxpool (n, c, h, w) -> (n, c)"),
        nn.Linear(in_features=hdim, out_features=hdim),
        nn.Dropout(),
        nn.ReLU(),
        nn.Linear(in_features=hdim, out_features=ODIM),
    ]
    return nn.Sequential(*head, *body, *tail)


def preprocess(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    X_out = np.empty(shape=(X.shape[0], IMAGE_SIZE * IMAGE_SIZE), dtype=np.float32)
    for row, im in enumerate(X.reshape((-1, 28, 28))):
        X_out[row, :] = cv2.resize(im, dsize=(IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_LINEAR).flatten()
    return X_out.reshape((-1, 1, IMAGE_SIZE, IMAGE_SIZE)).astype(np.float32), y.astype(np.int64)


if __name__ == "__main__":
    model = create_model(hdim=HDIM, image_size=IMAGE_SIZE, kernel_size=KERNEL_SIZE)
    print(model)
    print(util.dim(model))
    mnist.train(preprocess, model)
