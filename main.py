import time
from typing import Any, Iterable

import transform

from functools import reduce

if __name__ == "__main__":

    @transform.t_flat_map
    def m1(item: Any) -> Iterable:
        for i in range(item):
            yield item


    @transform.t_filter
    def m2(item: Any) -> bool:
        return item % 2 == 0


    @transform.t_map
    def m3(item: Any) -> Any:
        return item - 1


    n = 3000
    m = m3 * m2 * m1  # same as m3(m2(m1)))
    t0 = time.perf_counter()
    s1 = reduce(lambda x, y: x + y, m(range(n)))
    t1 = time.perf_counter()
    print(t1-t0)


    @transform.t_flat_map
    def m1(item: Any) -> Iterable:
        for i in range(item):
            yield item


    def m2(item: Any) -> bool:
        return item % 2 == 0


    def m3(item: Any) -> Any:
        return item - 1

    t0 = time.perf_counter()
    s1 = reduce(lambda x, y: x + y, map(m3, filter(m2, m1(range(n)))))
    t1 = time.perf_counter()
    print(t1 - t0)
