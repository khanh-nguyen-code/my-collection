from my_collection import ddb, transform

if __name__ == "__main__":
    c = ddb.Client(addr=ddb.Addr(host="localhost", port=3000))
    path = "file1"
    for i in range(10):
        key = f"key{i}"
        val = i
        c.post(path, key, key)
    for i in range(10):
        key = f"key{i}"
        val = c.get(path, key)
        print(val)


    @transform.t_map
    def split(val: str) -> int:
        return int(val[len("key"):])


    @transform.t_filter
    def keep_odd(val: int) -> bool:
        return val % 2 == 1


    val = c.transform(path, transform_func=keep_odd * split, reduce_func=lambda a, b: a + b)
    print(val)

    for i in range(10):
        key = f"key{i}"
        c.delete(path, key)
    for i in range(10):
        key = f"key{i}"
        val = c.get(path, key)
        if len(val) > 0:
            print(val)