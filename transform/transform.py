from __future__ import annotations

from functools import reduce
from typing import Iterable, Callable, Any, List


class Transform:
    handler: Callable[[Iterable], Iterable]

    def __init__(self, handler: Callable[[Iterable], Iterable]):
        self.handler = handler

    def __call__(self, i: Iterable) -> Iterable:
        return self.handler(i)

    def __add__(self, other: Transform) -> Transform:
        def helper(i: Iterable) -> Iterable:
            return other.handler(self.handler(i))

        return Transform(handler=helper)


def flat_map(handler: Callable[[Any], Iterable]) -> Transform:
    def helper(i: Iterable) -> Iterable:
        for item0 in i:
            for item1 in handler(item0):
                yield item1

    return Transform(handler=helper)


def map(handler: Callable[[Any], Any]) -> Transform:
    def helper(i: Iterable) -> Iterable:
        for item0 in i:
            item1 = handler(item0)
            yield item1

    return Transform(handler=helper)


def filter(handler: Callable[[Any], bool]) -> Transform:
    def helper(i: Iterable) -> Iterable:
        for item0 in i:
            if handler(item0):
                yield item0

    return Transform(handler=helper)


if __name__ == "__main__":
    @flat_map
    def m1(item: Any) -> Iterable:
        for i in range(item):
            yield item


    @filter
    def m2(item: Any) -> bool:
        return item % 2 == 0


    @map
    def m3(item: Any) -> Any:
        return item - 1

    n = 1000
    s1 = reduce(lambda x, y: x + y, (m1 + m2 + m3)(range(n)))
    import numpy as np
    a = np.arange(0, n, 2)
    s2 = (a * a).sum() - a.sum()
    print(s2-s1)
