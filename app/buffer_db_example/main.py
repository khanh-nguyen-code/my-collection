import os
import random
import string
import time
from typing import Optional, Any, Callable

from my_collection import buffer_db


def random_string(min_length: int, max_length: int) -> str:
    length = random.randrange(min_length, max_length)
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def p(p: int, handle: Callable, *data: Any):
    num_rounds = len(data[0])
    sort = [0.0 for _ in range(int(num_rounds * (100 - p) / 100))]
    for i in range(num_rounds):
        args = [data[j][i] for j in range(len(data))]
        t0 = time.perf_counter()
        handle(*args)
        t1 = time.perf_counter()
        dt = t1 - t0
        if dt < sort[0]:
            continue
        for k in range(len(sort)):
            if sort[k] <= dt:
                sort[:k] = sort[1:k + 1]
                sort[k] = dt
                break
    return sort[0]


def main(path: Optional[str] = "data.db", p_count: int = 95):
    if path is None:
        file = buffer_db.Buffer()
    else:
        if not os.path.exists(path):
            open(path, "wb").close()
        # r : open for reading
        # + : open a disk file for updating (reading and writing)
        # b : binary mode
        file = open(path, "r+b")

    db = buffer_db.DB(file=file, block_size=32 * 1024)

    with db.context() as ctx:
        print(f"stats: {db.stats()}")

        max_length = 64 * 1024
        min_length = 16

        num_keys = 1200
        write1_keys = range(0, 2 * num_keys // 3)
        delete1_keys = random.choices(write1_keys, k=len(write1_keys) // 2)
        write2_keys = random.choices(write1_keys, k=len(write1_keys) // 2) + list(range(2 * num_keys // 3, num_keys))
        read1_keys = range(num_keys)

        # write 8000 keys
        val_list = [random_string(min_length, max_length).encode("utf-8") for _ in range(len(write1_keys))]
        p_val = p(p_count, ctx.write, [f"key_{k}" for k in write1_keys], val_list)
        print(f"write1 p{p_count} {p_val * 1000000} μs")
        print(f"stats: {db.stats()}")

        # delete 4000 keys
        p_val = p(p_count, ctx.delete, [f"key_{k}" for k in delete1_keys])
        print(f"delete1 p{p_count} {p_val * 1000000} μs")
        print(f"stats: {db.stats()}")

        # write 8000 keys
        val_list = [random_string(min_length, max_length).encode("utf-8") for _ in range(len(write2_keys))]
        p_val = p(p_count, ctx.write, [f"key_{k}" for k in write2_keys], val_list)
        print(f"write2 p{p_count} {p_val * 1000000} μs")
        print(f"stats: {db.stats()}")

        # read 12000 keys
        p_val = p(p_count, ctx.read, [f"key_{k}" for k in read1_keys])
        print(f"read1 p{p_count} {p_val * 1000000} μs")
        print(f"stats: {db.stats()}")

    file.close()


if __name__ == "__main__":
    main()
