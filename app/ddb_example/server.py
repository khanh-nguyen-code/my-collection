import uvicorn

from my_collection import ddb

if __name__ == "__main__":
    import threading

    t_list = []
    storage_list = [
        ddb.Addr(host="localhost", port=3001),
        ddb.Addr(host="localhost", port=3002),
        ddb.Addr(host="localhost", port=3003),
        ddb.Addr(host="localhost", port=3004),
    ]
    for i, addr in enumerate(storage_list):
        t = threading.Thread(target=uvicorn.run, args=(ddb.Storage(f"data_{i}.db").app,), kwargs=addr.dict())
        t.start()
        t_list.append(t)
    addr = ddb.Addr(host="localhost", port=3000)
    t = threading.Thread(target=uvicorn.run, args=(ddb.Server(storage_list).app,), kwargs=addr.dict())
    t.start()
    t_list.append(t)
    for t in t_list:
        t.join()
