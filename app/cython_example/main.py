import numpy as np

from testmodule import py_int, py_string, py_arr

if __name__ == "__main__":
    i1 = 1234
    s1 = "1234"
    a1 = np.array([
        [1, 2],
        [3, 4],
    ], dtype=np.double)
    i2 = py_int(i1)
    s2 = py_string(s1)
    a2 = py_arr(a1)

    print(i1, i2)
    print(s1, s2)
    print(a1.flatten(), a2.flatten())
