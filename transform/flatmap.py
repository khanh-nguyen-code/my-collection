from __future__ import annotations

from functools import reduce
from typing import Callable, Any, Iterable

FlatMapFunc = Callable[[Any], Iterable]


class FlatMap:
    def __init__(self, func: FlatMapFunc):
        self.func = func

    def __add__(self, other: FlatMap) -> FlatMap:
        def helper(item0: Any) -> Iterable:
            item1_iter = self.func(item0)
            for item1 in item1_iter:
                item2_iter = other.func(item1)
                yield from item2_iter

        return FlatMap(helper)

    def __call__(self, item0_iter: Iterable) -> Iterable:
        for item0 in item0_iter:
            item1_iter = self.func(item0)
            yield from item1_iter


if __name__ == "__main__":
    @FlatMap
    def m1(item: Any) -> Iterable:
        for i in range(item):
            yield item


    @FlatMap
    def m2(item: Any) -> Iterable:
        if item % 2 == 0:
            yield item


    @FlatMap
    def m3(item: Any) -> Iterable:
        yield item - 1


    print(reduce(lambda x, y: x + y, (m1 + m2 + m3)(range(1000))))
