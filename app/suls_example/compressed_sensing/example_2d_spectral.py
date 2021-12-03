from typing import Optional, List

import numpy as np
from khanh_utils import suls
from PIL import Image
from matplotlib import pyplot as plt
from pathos.multiprocessing import ProcessPool

from app.suls_example.compressed_sensing import basis
from app.suls_example.compressed_sensing.basis.laplacian import create_grid_adj_matrix

"""
this example recovers an image with missing pixels
by transforming the image into frequency domain (fourier or laplace).
assuming in frequency domain, the signal is sparse,
use compressed sensing to reconstruct the image
"""


def mat_stack(mat: List[List[np.ndarray]]) -> np.ndarray:
    """
    [[A, B],
     [C, D]]
    """
    row_list = []
    for mat_row in mat:
        row = np.hstack(mat_row)
        row_list.append(row)
    out = np.vstack(row_list)
    return out


def reconstruct_real(
        measure_signal: np.ndarray,
        measure_matrix: np.ndarray,
        inverse_transform_matrix: np.ndarray,
) -> np.ndarray:
    """
    reconstruct_complex
    :param measure_signal:
    :param measure_matrix:
    :param inverse_transform_matrix:
    :return: reconstruct signal
    """
    measure_signal = measure_signal.astype(np.float64)
    measure_matrix = measure_matrix.astype(np.float64)
    inverse_transform_matrix = inverse_transform_matrix.astype(np.float64)
    #
    A = measure_matrix @ inverse_transform_matrix
    y = suls.solve_lp(A, measure_signal)
    reconstruct_signal = inverse_transform_matrix @ y
    return reconstruct_signal


def reconstruct_complex(
        measure_signal: np.ndarray,
        measure_matrix: np.ndarray,
        inverse_transform_matrix: np.ndarray,
) -> np.ndarray:
    """
    reconstruct_complex
    :param measure_signal:
    :param measure_matrix:
    :param inverse_transform_matrix:
    :return: reconstruct signal
    """
    measure_signal = measure_signal.astype(np.complex128)
    measure_matrix = measure_matrix.astype(np.complex128)
    inverse_transform_matrix = inverse_transform_matrix.astype(np.complex128)
    #
    A = measure_matrix @ inverse_transform_matrix
    n, m = A.shape
    F = mat_stack([
        [np.real(A), -np.imag(A)],
        [np.imag(A), np.real(A)],
    ]).astype(np.float64)
    x = mat_stack([
        [measure_signal.real],
        [measure_signal.imag],
    ]).flatten()
    y = suls.solve_lp(F, x)
    f = np.empty(shape=(m,), dtype=np.complex128)
    f.real, f.imag = y[0:m], y[m:2 * m]
    reconstruct_signal = inverse_transform_matrix @ f
    return reconstruct_signal


def create_random_measure_matrix(d: int, n: int) -> np.ndarray:
    """
    create_measure_matrix
    :param d: number of measure signal data points
    :param n: number of true signal data points
    :return: measure matrix
    """
    M = np.zeros(shape=(d, n), dtype=np.int64)
    indices = np.random.choice(np.arange(n), size=d, replace=False)
    for i in range(d):
        M[i, indices[i]] = 1
    return M


def open_im(filename: str, height: Optional[int] = None, width: Optional[int] = None) -> np.ndarray:
    im = Image.open(filename).convert("RGB")
    if height is not None and width is not None:
        im.thumbnail(size=(width, height), resample=Image.ANTIALIAS)
    im = np.array(im)
    return im


if __name__ == "__main__":
    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(16.0, 4.0))
    ax = ax.flatten()
    ax_index = 0

    height, width, channel = 0, 0, 0


    def draw_im(im: np.ndarray, title: str = "im"):
        global ax_index
        ax[ax_index].imshow(im)
        ax[ax_index].set_title(title)
        ax_index += 1


    def im2sig(im: np.ndarray) -> np.ndarray:
        signal = im.reshape((height * width, channel))
        return signal


    def sig2im(signal: np.ndarray) -> np.ndarray:
        signal = signal.real.astype(np.float64)  # take real part
        signal += 0.5
        signal[signal < 0] = 0
        signal[signal > 255] = 255
        signal = signal.astype(np.uint8)
        im = signal.reshape((height, width, channel))
        return im


    # open true im
    true_im = open_im(filename="example_2d_spectral.png", height=32, width=32)
    draw_im(true_im, "true signal")
    height, width, channel = true_im.shape
    true_signal = im2sig(true_im)

    # create measure im
    N = len(true_signal)
    D = int(0.5 * N)
    measure_matrix = create_random_measure_matrix(D, N)
    measure_signal = measure_matrix @ true_signal
    measure_im = sig2im(measure_matrix.T @ measure_signal)
    draw_im(measure_im, "measure signal")

    # reconstruct true im
    pool = ProcessPool()

    _, inverse_fourier_matrix = basis.fourier_2d(height, width, height, width)
    reconstruct_signal_fourier = pool.amap(
        reconstruct_complex,
        [measure_signal[:, c] for c in range(channel)],
        [measure_matrix for _ in range(channel)],
        [inverse_fourier_matrix for _ in range(channel)]
    )

    adj = create_grid_adj_matrix(height, width)
    _, inverse_laplacian_matrix = basis.laplacian(adj)
    reconstruct_signal_laplacian = pool.amap(
        reconstruct_real,
        [measure_signal[:, c] for c in range(channel)],
        [measure_matrix for _ in range(channel)],
        [inverse_laplacian_matrix for _ in range(channel)]
    )
    reconstruct_signal_fourier = reconstruct_signal_fourier.get()
    reconstruct_signal_fourier = np.array(reconstruct_signal_fourier).T
    draw_im(sig2im(reconstruct_signal_fourier), "reconstruct signal (fourier basis)")

    reconstruct_signal_laplacian = reconstruct_signal_laplacian.get()
    reconstruct_signal_laplacian = np.array(reconstruct_signal_laplacian).T
    draw_im(sig2im(reconstruct_signal_laplacian), "reconstruct signal (laplacian basis)")

    # draw
    fig.suptitle(f"image size: {height} x {width}")
    plt.tight_layout()
    plt.show()
