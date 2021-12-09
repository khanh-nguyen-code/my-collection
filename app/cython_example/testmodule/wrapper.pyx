#cython: language_level=3
cimport libc.stdint as stdint

cdef extern from "lib/testmodule.h":
    int c_int(int in_int)
    char* c_string(char* in_string)
    void c_ptr(stdint.uint64_t h, stdint.uint64_t w, double* in_arr, double* out_arr)

cimport libc.stdlib as stdlib
cimport libc.string as string
import numpy as np

def py_int(in_int: int) -> int:
    return c_int(in_int)

def py_string(in_string: str, encoding: str="utf-8", errors: str="strict") -> str:
    in_bytes: bytes = in_string.encode(encoding=encoding, errors=errors)

    cdef char* c_in_string = <char*> stdlib.malloc(1 + <Py_ssize_t> len(in_bytes))
    cdef char* c_out_string

    string.strcpy(c_in_string, in_bytes)

    try:
        c_out_string = c_string(c_in_string)
        out_bytes: bytes = c_out_string[:] # copy
        return out_bytes.decode(encoding=encoding, errors=errors)
    finally:
        stdlib.free(c_in_string)
        stdlib.free(c_out_string)


def py_arr(in_arr: np.ndarray) -> np.ndarray:
    if len(in_arr.shape) != 2:
        raise Exception("shape")
    if in_arr.dtype != np.double:
        raise Exception("dtype")

    out_arr = np.empty_like(in_arr)

    cdef stdint.uint64_t h = in_arr.shape[0]
    cdef stdint.uint64_t w = in_arr.shape[1]
    cdef double[:, :] in_arr_buf = np.ascontiguousarray(in_arr)
    cdef double[:, :] out_arr_buf = np.ascontiguousarray(out_arr)

    c_ptr(h, w, &in_arr_buf[0, 0], &out_arr_buf[0, 0])

    return out_arr
