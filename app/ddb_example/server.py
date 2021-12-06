import multiprocessing as mp

import uvicorn

from my_collection import ddb


def run_storage(addr: ddb.Addr):
    uvicorn.run(ddb.Storage(f"data_{addr.port}.db").app, host=addr.host, port=addr.port)


def run_server(addr: ddb.Addr, storage_list: ddb.Addr):
    uvicorn.run(ddb.Server(storage_list).app, host=addr.host, port=addr.port)


if __name__ == "__main__":

    p_list = []
    num_storages = 4

    storage_list = [ddb.Addr(host="localhost", port=3000 + i) for i in range(num_storages)]
    for addr in storage_list:
        p = mp.Process(target=run_storage, args=(addr,))
        p_list.append(p)
        p.start()

    addr = ddb.Addr(host="localhost", port=2999)
    p = mp.Process(target=run_server, args=(addr, storage_list))
    p.start()
    p_list.append(p)
    for p in p_list:
        p.join()
