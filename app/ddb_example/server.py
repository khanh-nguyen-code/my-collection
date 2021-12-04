import uvicorn

from my_collection import ddb

if __name__ == "__main__":
    import threading

    t_list = []
    num_storages = 4

    storage_list = [ddb.Addr(host="localhost", port=3000 + i) for i in range(num_storages)]
    for i, addr in enumerate(storage_list):
        t = threading.Thread(target=uvicorn.run, args=(ddb.Storage(f"data_{i}.db", block_size=32).app,), kwargs=addr.dict())
        t.start()
        t_list.append(t)
    addr = ddb.Addr(host="localhost", port=2999)
    t = threading.Thread(target=uvicorn.run, args=(ddb.Server(storage_list).app,), kwargs=addr.dict())
    t.start()
    t_list.append(t)
    for t in t_list:
        t.join()
