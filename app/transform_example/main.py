from functools import reduce

from my_collection.transform import t_flat_map, t_filter, t_map

if __name__ == "__main__":
    n = 1000
    m3 = t_map(lambda item: item - 1)
    m2 = t_filter(lambda item: item % 2 == 0)
    m1 = t_flat_map(lambda item: (item for _ in range(item)))
    s1 = reduce(lambda x, y: x + y, (m3 * m2 * m1)(range(n)))
    import numpy as np

    a = np.arange(0, n, 2)
    s2 = (a * a).sum() - a.sum()
    print(s2 - s1)
