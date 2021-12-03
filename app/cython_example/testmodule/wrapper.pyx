#cython: language_level=3
cdef extern from "lib/testmodule.h":
    int c_int(int in_int)
    char* c_string(char* in_string)
    void c_ptr(int h, int w, double* in_arr, double* out_arr)

cimport libc.stdlib as stdlib
import numpy as np

def py_int(in_int: int) -> int:
    return c_int(in_int)

def py_string(in_string: str) -> str:
    cdef char* c_out_string = c_string(in_string.encode("utf-8"))
    try:
        return c_out_string.decode("utf-8")
    finally:
        stdlib.free(c_out_string)

def py_arr(in_arr: np.ndarray) -> np.ndarray:
    if len(in_arr.shape) != 2:
        raise Exception("shape")
    if in_arr.dtype != np.double:
        raise Exception("dtype")

    h, w = in_arr.shape

    out_arr = np.empty_like(in_arr)

    cdef double[:, :] in_arr_buf = np.ascontiguousarray(in_arr)
    cdef double[:, :] out_arr_buf = np.ascontiguousarray(out_arr)

    c_ptr(h, w, &in_arr_buf[0, 0], &out_arr_buf[0, 0])

    return out_arr