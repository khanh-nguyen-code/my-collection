import math
import multiprocessing as mp
import queue
import threading
import time
from typing import Tuple, Iterable

import matplotlib.animation as animation
import matplotlib.pyplot as plt


def _iter_from_queue(q: mp.Queue) -> Iterable:
    while True:
        try:
            yield q.get()
        except queue.Empty:
            return


def _animation_routine(names: Tuple[str, ...], q: mp.Queue):
    fig, axes = plt.subplots(ncols=1, nrows=len(names))
    axes[-1].set_xlabel("iteration")
    ax_dict = {name: ax for name, ax in zip(names, axes)}
    line_dict = {name: ax.plot([], [])[0] for name, ax in ax_dict.items()}
    for name, ax in ax_dict.items():
        ax.set_title(name)

    def draw_frame(data, *fargs) -> Iterable[plt.Artist]:
        # data: Dict[str, Tuple[List[int], List[float]]]
        all_indices = []
        for name, (indices, values) in data.items():
            all_indices.extend(indices)
        if len(all_indices) == 0:
            return ()

        min_index = min(all_indices)
        max_index = max(all_indices)

        for name, (indices, values) in data.items():
            if name not in names:
                continue
            if len(indices) == 0:
                continue
            ax = ax_dict[name]
            ax.set_xlim(min_index - 1, max_index + 1)
            ax.set_ylim(math.floor(min(values)), math.ceil(max(values)))

            line = line_dict[name]
            line.set_data(indices, values)
        return line_dict.values()

    anim = animation.FuncAnimation(
        fig=fig,  # figure to draw on
        blit=False,  # set False to resize the ax
        func=draw_frame,  # being called in each frame
        frames=_iter_from_queue(q),  # yields frame
        interval=10,  # delay between frames (ms)
        fargs=(),  # passed to func
        repeat=False,  # repeat the animation
        repeat_delay=0,  # delay between animation runs
    )
    plt.tight_layout()
    plt.show()


class Plot:
    def __init__(self, *names: str):
        self.names = names
        self.frame_queue = mp.Queue(maxsize=1)
        self.index = 0
        self.data = {name: [[], []] for name in self.names}
        self.draw_process = mp.Process(target=_animation_routine, args=(self.names, self.frame_queue))
        self.draw_process.start()
        self.insert_thread = threading.Thread(target=Plot._insert_routine, args=(self,))
        self.insert_thread.start()

    def __del__(self):
        self.insert_thread.join()
        self.draw_process.join()

    def insert(self, **kwargs):
        for name, value in kwargs.items():
            if name in self.data:
                self.data[name][0].append(self.index)
                self.data[name][1].append(value)
        self.index += 1

    def _insert_routine(self):
        # must be thread
        while True:
            self.frame_queue.put(self.data)


if __name__ == "__main__":
    p = Plot("sin", "cos")
    x = 0.0
    i = 0
    while True:
        i += 1
        if i % 2 == 0:
            p.insert(sin=math.sin(x))
        else:
            p.insert(cos=math.cos(x))
        x += 0.1
        time.sleep(0.5)
    pass
