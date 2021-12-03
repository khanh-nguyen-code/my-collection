from typing import Optional, List

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from pathos.multiprocessing import ProcessPool

from my_collection import suls


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


def open_im(filename: str, height: Optional[int] = None, width: Optional[int] = None) -> np.ndarray:
    im = Image.open(filename).convert("RGB")
    if height is not None and width is not None:
        im.thumbnail(size=(width, height), resample=Image.ANTIALIAS)
    im = np.array(im)
    return im


if __name__ == "__main__":

    def draw_im(im1: np.ndarray, im2: np.ndarray, title: str = ""):
        _, ax = plt.subplots(nrows=1, ncols=2, figsize=(8.0, 4.0))
        plt.suptitle(f"image size {im1.shape[0]}x{im1.shape[1]}")
        ax[0].imshow(im1)
        ax[1].imshow(im2)
        ax[1].set_title(title)
        plt.show()


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


    true_im = open_im(filename="example_2d_spatial.png", height=32, width=32)
    draw_im(true_im, true_im, "true signal")
    height, width, channel = true_im.shape

    true_signal = im2sig(true_im)

    A_list = []
    b_list = []

    pool = ProcessPool()
    while True:
        # measure
        m = np.random.randint(low=0, high=2, size=(height * width)).astype(np.float64)
        b = m @ true_signal
        A_list.append(m)
        b_list.append(b)
        if len(b_list) % 100 == 0:
            # reconstruct
            reconstruct_signal = pool.map(
                suls.solve_lp,
                [np.array(A_list) for _ in range(channel)],
                [np.array(b_list)[:, i] for i in range(channel)],
            )
            reconstruct_signal = np.array(reconstruct_signal).T
            reconstruct_im = sig2im(reconstruct_signal)

            draw_im(true_im, reconstruct_im, f"no measurements {len(b_list)}")
