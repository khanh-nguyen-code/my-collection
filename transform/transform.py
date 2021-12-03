from __future__ import annotations

from typing import Iterable, Callable, Any, Union


class Transform:
    handler: Callable[[Iterable], Iterable]

    def __init__(self, handler: Callable[[Iterable], Iterable]):
        self.handler = handler

    def __call__(self, arg: Union[Iterable, Transform]) -> Union[Iterable, Transform]:
        if isinstance(arg, Iterable):
            return self.handler(arg)
        if isinstance(arg, Transform):
            def helper(i: Iterable) -> Iterable:
                return self.handler(arg.handler(i))

            return Transform(handler=helper)

    def __mul__(self, other: Transform) -> Transform:
        return self(other)


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

    from functools import reduce


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
    m = m3 * m2 * m1  # same as m3(m2(m1)))
    s1 = reduce(lambda x, y: x + y, m(range(n)))
    import numpy as np

    a = np.arange(0, n, 2)
    s2 = (a * a).sum() - a.sum()
    print(s2 - s1)
