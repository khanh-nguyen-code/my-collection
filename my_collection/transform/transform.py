from __future__ import annotations

from typing import Iterable, Callable, Any


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
