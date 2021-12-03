from __future__ import annotations

from typing import Iterable, Callable, Any, Union


class Transform:
    handler: Callable[[Iterable], Iterable]

    def __init__(self, handler: Callable[[Iterable], Iterable]):
        self.handler = handler

    def __call__(self, i: Iterable) -> Iterable:
        return self.handler(i)

    def __mul__(self, other: Transform) -> Transform:
        return Transform(handler=lambda i: self.handler(other.handler(i)))


def t_flat_map(handler: Callable[[Any], Iterable]) -> Transform:
    def helper(i: Iterable) -> Iterable:
        for item0 in i:
            yield from handler(item0)

    return Transform(handler=helper)


def t_map(handler: Callable[[Any], Any]) -> Transform:
    return Transform(handler=lambda i: map(handler, i))


def t_filter(handler: Callable[[Any], bool]) -> Transform:
    return Transform(handler=lambda i: filter(handler, i))


if __name__ == "__main__":

    from functools import reduce


    @t_flat_map
    def m1(item: Any) -> Iterable:
        for i in range(item):
            yield item


    @t_filter
    def m2(item: Any) -> bool:
        return item % 2 == 0


    @t_map
    def m3(item: Any) -> Any:
        return item - 1


    n = 1000
    m = m3 * m2 * m1
    s1 = reduce(lambda x, y: x + y, m(range(n)))
    import numpy as np

    a = np.arange(0, n, 2)
    s2 = (a * a).sum() - a.sum()
    print(s2 - s1)
