import numpy as np

from testmodule import py_int, py_string, py_arr

if __name__ == "__main__":
    print(py_int(3))
    print(py_string("3"))
    print(py_arr(np.array([
        [1, 2],
        [3, 4],
    ], dtype=np.double)))
