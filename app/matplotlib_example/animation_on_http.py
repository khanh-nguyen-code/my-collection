import queue
import threading
from typing import Iterable, Iterator, Tuple, Optional

import fastapi
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pydantic
import uvicorn
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from my_collection import http

fig: Optional[Figure] = None
ctx = http.Context()
q = queue.Queue(maxsize=1)


class Point(pydantic.BaseModel):
    line: str
    data: Tuple[float, float]


def run_animation(q: queue.Queue, ax: Axes) -> FuncAnimation:
    def data_iter_func() -> Iterable[dict[str, np.ndarray]]:
        storage: dict[str, np.ndarray] = {}
        while True:
            try:
                point = q.get(block=True, timeout=0.001)
                # if not queue.Empty
                if point.line not in storage:
                    storage[point.line] = np.array((point.data,), dtype=np.float64)
                else:
                    storage[point.line] = np.concatenate((storage[point.line], (point.data,)), axis=0)
            except queue.Empty:
                pass
            yield storage

    data_iter: Iterator[dict[str, np.ndarray]] = iter(data_iter_func())

    artist: dict[str, Line2D] = {}

    def draw_call(_: int) -> Iterable[Artist]:
        min_x = -1
        max_x = +1
        min_y = -1
        max_y = +1
        for name, data in next(data_iter).items():
            if name not in artist:
                artist[name] = ax.plot((), (), label=name)[0]
                artist[name].set_linewidth(1)
                artist[name].set_markersize(3)
                artist[name].set_label(name)
                ax.legend()
            artist[name].set_data(data.T)
            min_x = min(min_x, min(data[:, 0]))
            max_x = max(max_x, max(data[:, 0]))
            min_y = min(min_y, min(data[:, 1]))
            max_y = max(max_y, max(data[:, 1]))

        min_x -= 1
        max_x += 1
        min_y -= 1
        max_y += 1

        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)

        return [a for a in artist.values()]

    ani = FuncAnimation(
        fig=fig,
        func=draw_call,
        blit=False,
        repeat=False,
        interval=1,
    )
    return ani


class Request(pydantic.BaseModel):
    x: float
    y: float


class Server(http.Server):
    def __init__(self):
        super(Server, self).__init__(ctx)

    @ctx.http_method(ctx.method_post, "/post/{line}")
    def post_point(
            self,
            line: str = fastapi.Path(default=""),
            request: Request = fastapi.Body(default=None),
    ):
        q.put(Point(line=line, data=(request.x, request.y)))

    @ctx.http_method(ctx.method_get, "/line", response_class=fastapi.responses.HTMLResponse)
    def get_line(self):
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Animation</title>
        </head>
        <body>
            {mpld3.fig_to_html(fig)}
        </body>
        </html>
        """


if __name__ == "__main__":
    ax: Axes
    fig, ax = plt.subplots()
    ax.set_title("animation")
    server = Server()
    threading.Thread(target=uvicorn.run, args=(server.app,), kwargs={"port": 3000}).start()
    ani = run_animation(q, ax)
    plt.tight_layout()
    plt.show()
