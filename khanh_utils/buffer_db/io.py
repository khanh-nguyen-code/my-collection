import os
from typing import Union, Optional


class IO:
    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        raise NotImplemented

    def read(self, n: Optional[int] = None) -> bytes:
        raise NotImplemented

    def write(self, b: Union[bytes, bytearray]):
        raise NotImplemented

    def truncate(self, size: Optional[int] = None) -> int:
        raise NotImplemented


class Buffer(IO):
    buffer: bytearray
    index: int

    def __init__(self, buffer: Union[bytes, bytearray] = b""):
        self.buffer = bytearray(buffer)
        self.index = 0

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            self.index = offset
        elif whence == os.SEEK_CUR:
            self.index += offset
        elif whence == os.SEEK_END:
            self.index = len(self.buffer) + offset
        else:
            raise Exception("seek whence")
        return self.index

    def read(self, n: Optional[int] = None) -> bytes:
        if n is None:
            n = len(self.buffer)
        out = bytes(self.buffer[self.index:self.index + n])
        self.index += n
        return out

    def write(self, b: Union[bytes, bytearray]):
        self.buffer += b"\0" * max(0, self.index + len(b) - len(self.buffer))
        self.buffer[self.index:self.index + len(b)] = b
        self.index += len(b)

    def truncate(self, size: Optional[int] = None) -> int:
        if size is not None:
            self.seek(size)
        self.buffer = self.buffer[:self.index]
        return self.index
