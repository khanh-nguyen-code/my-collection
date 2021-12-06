import time
from typing import Tuple

import cvxpy as cp
import numpy as np

from my_collection import logger


def assert_arguments(A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    assert len(A.shape) == 2, "A must be matrix"
    assert len(b.shape) == 1, "b must be vector"
    assert A.shape[0] == b.shape[0], "A rows must equal b dims"
    assert A.shape[0] < A.shape[1], "A must be fat, under determined"
    assert (~np.isreal(A)).sum() == 0, "A must be real"
    assert (~np.isreal(b)).sum() == 0, "b must be real"
    return A.astype(np.float64), b.astype(np.float64)


def solve_lp(A: np.ndarray, b: np.ndarray, p: int = 1, a: float = 0.01) -> np.ndarray:
    """
    Minimizer of ||x||_p
    Given Ax=b
    By minimizing ||Ax-b||_2^2 + a||x||_p
    """

    A, b = assert_arguments(A, b)
    m, n = A.shape

    t1 = time.time()
    x = cp.Variable(shape=(n,))
    objective = cp.Minimize(cp.sum_squares(A @ x - b) + a * cp.norm(x, p))
    problem = cp.Problem(objective=objective)
    t2 = time.time()
    logger.now().debug(f"model building... {t2 - t1}s")
    problem.solve()
    t3 = time.time()
    logger.now().debug(f"model solving.... {t3 - t2}s")
    return x.value


def solve_l1(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Minimizer of ||x||_1
    Given Ax=b

    Linear program
    Minimize 1^T y (sum of all elements of y)
    Given y >= |x| and Ax=b
    """
    A, b = assert_arguments(A, b)
    m, n = A.shape
    t1 = time.time()
    x = cp.Variable(shape=(n,))
    y = cp.Variable(shape=(n,))
    problem = cp.Problem(
        objective=cp.Minimize(cp.sum(y)),
        constraints=[
            y >= x,
            y >= -x,
            A @ x == b,
        ]
    )
    t2 = time.time()
    logger.now().debug(f"model building... {t2 - t1}s")
    problem.solve()
    t3 = time.time()
    logger.now().debug(f"model solving.... {t3 - t2}s")
    return x.value
