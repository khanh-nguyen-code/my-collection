from typing import Iterable, Optional, Iterator, Tuple, List

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

if __name__ == "__main__":
    def data_iter_func(maxsize: Optional[int] = 1000) -> Iterable[Tuple[Tuple[np.ndarray, np.ndarray], float]]:
        blue_trajectory: List[Tuple[float, float]] = [(0, 0)]
        orange_trajectory: List[Tuple[float, float]] = [(0, 0)]
        while True:
            blue_move = tuple(np.random.normal(loc=0, scale=1, size=(2,)))
            orange_move = tuple(np.random.normal(loc=0, scale=1, size=(2,)))
            new_blue_point = (
                blue_trajectory[-1][0] + blue_move[0],
                blue_trajectory[-1][1] + blue_move[1],
            )
            new_orange_point = (
                orange_trajectory[-1][0] + orange_move[0],
                orange_trajectory[-1][1] + orange_move[1],
            )
            blue_trajectory.append(new_blue_point)
            orange_trajectory.append(new_orange_point)
            if maxsize is not None:
                if len(blue_trajectory) > maxsize:
                    blue_trajectory = blue_trajectory[-maxsize:]
                if len(orange_trajectory) > maxsize:
                    orange_trajectory = orange_trajectory[-maxsize:]
            data = np.array(blue_trajectory), np.array(orange_trajectory)
            max_r2 = np.max(np.sum(np.vstack(data) ** 2, axis=1))
            r = int(1 + 1.2 * np.sqrt(max_r2))
            yield data, r


    data_iter: Iterator[Tuple[Tuple[np.ndarray, np.ndarray], float]] = iter(data_iter_func())

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_aspect("equal")

    orange_artist: PathCollection = ax.scatter((), ())
    blue_artist: Line2D = ax.plot((), ())[0]

    orange_artist.set_color("C1")
    orange_artist.set_label("path_collection")

    blue_artist.set_color("C0")
    blue_artist.set_linewidth(1)
    blue_artist.set_label("line2d")


    def draw_call(i: int) -> Iterable[Artist]:
        ax.set_title(f"iteration {i}")

        (blue_data, orange_data), r = next(data_iter)

        ax.set_xlim(left=-r, right=+r)
        ax.set_ylim(bottom=-r, top=+r)

        orange_artist.set_offsets(orange_data)
        orange_artist.set_sizes(np.ones(shape=(orange_data.shape[0])))

        blue_artist.set_data(blue_data.T)

        yield orange_artist
        yield blue_artist


    ani = FuncAnimation(
        fig=fig,
        func=draw_call,
        blit=True,
        repeat=False,
        interval=1,
    )

    plt.legend()
    plt.tight_layout()
    plt.show()
