import os
import pickle
import random
from typing import Tuple, Callable, List

import numpy as np
import torch
from sklearn.datasets import fetch_openml
from torch import nn, optim

from plot import Plot


def load_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    :return: (X, y) where X is a float32 matrix of size (70000, 784) and y is a int64 vector of size (70000,)
    """
    if not os.path.exists("mnist.pickle"):
        X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
        X, y = X.astype(np.float32), y.astype(np.int64)
        pickle.dump((X, y), open("mnist.pickle", "wb"))
    else:
        X, y = pickle.load(open("mnist.pickle", "rb"))
    return X, y


def train(preprocess: Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]], model: nn.Module):
    X, y = preprocess(*load_data())
    # train - test split
    num_samples = X.shape[0]
    indices = np.random.permutation(num_samples)
    num_train_samples = int(num_samples * 0.7)
    num_test_samples = num_samples - num_train_samples
    train_indices = [*indices[: num_train_samples]]  # create new object to shuffle
    test_indices = indices[num_train_samples: num_train_samples + num_test_samples]
    # precompute test_label
    test_label = [y[i] for i in test_indices]

    def accuracy(pred: List[int], label: List[int]) -> float:
        assert len(pred) == len(label)
        correct = sum(map(lambda pair: pair[0] == pair[1], zip(pred, label)))
        return correct / len(label)

    def decode(indices: List[int]) -> List[int]:
        model.eval()
        with torch.no_grad():
            out = []
            for i in indices:
                x_ = torch.from_numpy(X[i:i + 1])
                logits = model.forward(x_).detach().cpu().numpy()
                out.append(np.argmax(logits, axis=1)[0])
            return out

    plot = Plot("loss", "train_accuracy", "test_accuracy")
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for epoch in range(1000):
        model.train()
        random.shuffle(train_indices)
        loss_v = 0.0
        for count, i in enumerate(train_indices):
            model.zero_grad()
            x_ = torch.from_numpy(X[i:i + 1])
            y_ = torch.from_numpy(y[i:i + 1])
            out = model.forward(x_)
            loss = nn.CrossEntropyLoss().forward(out, y_)
            loss.backward()
            optimizer.step()
            loss_v += float(loss.detach().cpu().numpy())
        loss_v /= len(train_indices)
        model.eval()
        train_label = [y[i] for i in train_indices]
        accuracy_v_train = accuracy(decode(train_indices), train_label)
        accuracy_v_test = accuracy(decode(test_indices), test_label)
        print(
            f"epoch {epoch + 1}: avg train loss {loss_v}, train accuracy {accuracy_v_train}, test accuracy {accuracy_v_test}")
        plot.insert(loss=loss_v, train_accuracy=accuracy_v_train, test_accuracy=accuracy_v_test)
