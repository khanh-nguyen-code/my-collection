from functools import reduce
from typing import Any, Iterable

from khanh_utils.transform import t_flat_map, t_filter, t_map

if __name__ == "__main__":

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
