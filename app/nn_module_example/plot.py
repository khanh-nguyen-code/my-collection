import math
import multiprocessing as mp
import threading
import time
from typing import Tuple, Iterable

import matplotlib.animation as animation
import matplotlib.pyplot as plt


class Plot:
    def __init__(self, *name: str):
        self.name = name
        self.frame_queue = mp.Queue(maxsize=1)
        self.data = [[] for _ in range(len(self.name))]
        self.draw_process = mp.Process(target=Plot._animation_routine, args=(self.name, self.frame_queue))
        self.draw_process.start()
        self.insert_thread = threading.Thread(target=Plot._insert_routine, args=(self,))
        self.insert_thread.start()

    def __del__(self):
        self.insert_thread.join()
        self.draw_process.join()

    def insert(self, **kwargs):
        point = []
        for name in self.name:
            point.append(kwargs[name])
        for d_idx in range(len(self.data)):
            self.data[d_idx].append(point[d_idx])

    def _insert_routine(self):
        # must be thread
        while True:
            self.frame_queue.put(self.data)

    @staticmethod
    def _animation_routine(name: Tuple[str, ...], q: mp.Queue):
        def points():
            while True:
                yield q.get()

        num_plots = len(name)
        fig, axes = plt.subplots(ncols=num_plots, nrows=1)
        axes[-1].set_xlabel("iteration")
        for ax, name in zip(axes, name):
            ax.set_title(name)
        line = [
            ax.plot([], [])[0]
            for ax in axes
        ]

        def draw_frame(data, *fargs) -> Iterable[plt.Artist]:
            for a_idx, ax in enumerate(axes):
                ax.set_xlim(0, 1 + len(data[a_idx]))
                ax.set_ylim(int(min([0, *data[a_idx]])), 1 + int(max([0, *data[a_idx]])))
            for a_idx, a in enumerate(line):
                a.set_data(
                    range(len(data[a_idx])),
                    data[a_idx],
                )
            return line

        anim = animation.FuncAnimation(
            fig=fig,  # figure to draw on
            blit=False,  # set False to resize the ax
            func=draw_frame,  # being called in each frame
            frames=points(),  # yields frame
            interval=10,  # delay between frames (ms)
            fargs=(),  # passed to func
            repeat=False,  # repeat the animation
            repeat_delay=0,  # delay between animation runs
        )
        plt.show()


if __name__ == "__main__":
    p = Plot("sin", "cos")
    x = 0.0
    while True:
        sin = math.sin(x)
        cos = math.cos(x)
        x += 0.1
        p.insert(sin=sin, cos=cos)
        time.sleep(0.1)
    pass
