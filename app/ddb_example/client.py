from typing import Any

import fastapi

from my_collection import ddb, transform

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
