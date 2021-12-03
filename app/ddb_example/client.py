import time
from functools import reduce
from typing import Any, Iterable

import fastapi

from my_collection import ddb, transform
from my_collection.transform import t_flat_map, t_map

if __name__ == "__main__":
    c = ddb.Client(addr=ddb.Addr(host="localhost", port=3000))
    path = "file1"
    try:

        c.remove(path)

        c.post(path, "key1", {"idx": 1})
        c.post(path, "key2", {"idx": 2})
        c.post(path, "key3", {"idx": 3})
        c.write(path, {
            "key4": {"idx": 4},
            "key5": {"idx": 5},
            "key6": {"idx": 6},
        })

        print("only key2", c.get(path, "key2"))
        print("all keys", c.read(path))


        @transform.t_map
        def get_i(val: Any) -> int:
            return val["idx"]


        @transform.t_filter
        def keep_odd(val: int) -> bool:
            return val % 2 == 1


        val = c.transform(path, transform_func=keep_odd * get_i, reduce_func=lambda a, b: a + b)

        print("sum of all odd numbers", val)

        c.delete(path, "key1")
        c.delete(path, "key2")
        c.delete(path, "key3")

        print("key 4 5 6", c.read(path))

        c.remove(path)

        print("empty", c.read(path))

    except fastapi.HTTPException as e:
        print(e.status_code, e.detail)

    path = "word_count.txt"
    try:
        with open(path) as f:
            data = {f"line_{i}": line.rstrip("\n") for i, line in enumerate(f) if len(line.rstrip("\n")) > 0}

        t0 = time.perf_counter()
        c.write(path, data)
        t1 = time.perf_counter()
        print("write time:", t1-t0)


        @t_flat_map
        def split(line: str) -> Iterable[str]:
            return line.split(" ")


        @t_map
        def to_count(word: str) -> int:
            return 1


        t0 = time.perf_counter()
        word_count = c.transform(path, to_count * split, lambda a, b: a + b)
        t1 = time.perf_counter()
        print("count time:", t1-t0)
        print(word_count)

        t0 = time.perf_counter()
        with open(path) as f:
            word_count = reduce(lambda a, b: a+b, (to_count * split)(line for i, line in enumerate(f) if len(line.rstrip("\n")) > 0))
        t1 = time.perf_counter()
        print("local count time:", t1-t0)
        print(word_count)

        # c.remove(path)

    except fastapi.HTTPException as e:
        print(e.status_code, e.detail)
