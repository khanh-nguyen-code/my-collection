from __future__ import annotations

import inspect
import sys
import time
from typing import Any, Callable, List, Tuple

Writer = Callable[[str, ], None]


class Context:
    __debug_writer: Writer
    __info_writer: Writer
    __error_writer: Writer
    __time_now: time.struct_time
    __kv_list: List[Tuple[str, Any]]

    def __init__(self,
                 info_writer: Writer,
                 error_writer: Writer,
                 debug_writer: Writer,
                 time_now: time.struct_time,
                 kv_list: List[Tuple[str, Any]],
                 ):
        self.__debug_writer = debug_writer
        self.__info_writer = info_writer
        self.__error_writer = error_writer
        self.__time_now = time_now
        self.__kv_list = kv_list

    def debug(self, msg: str):
        if self.__debug_writer is not None:
            self.__debug_writer(self.__to_log(msg))

    def info(self, msg: str):
        if self.__info_writer is not None:
            self.__info_writer(self.__to_log(msg))

    def error(self, msg: str):
        if self.__error_writer is not None:
            self.__error_writer(self.__to_log(msg))

    def with_field(self, key: str, val: Any) -> Context:
        return Context(
            info_writer=self.__info_writer,
            error_writer=self.__error_writer,
            debug_writer=self.__debug_writer,
            time_now=self.__time_now,
            kv_list=[*self.__kv_list, (key, val)],
        )

    def __to_log(self, msg: str) -> str:
        time_str = time.strftime('%Y/%m/%d %H:%M:%S', self.__time_now)
        field_str_list = [f"{key}={val}" for key, val in self.__kv_list]
        return "|".join([time_str, *field_str_list, msg]).rstrip("\n")


class Logger:
    __debug_writer: Writer
    __info_writer: Writer
    __error_writer: Writer

    def __init__(self, debug_writer: Writer = None, info_writer: Writer = None, error_writer: Writer = None):
        self.__debug_writer = debug_writer
        self.__info_writer = info_writer
        self.__error_writer = error_writer

    def now(self) -> Context:
        caller_frame: inspect.FrameInfo = inspect.getouterframes(inspect.currentframe(), 0)[1]
        return Context(
            debug_writer=self.__debug_writer,
            info_writer=self.__info_writer,
            error_writer=self.__error_writer,
            time_now=time.localtime(),
            kv_list=[("caller", f"{caller_frame.filename}:{caller_frame.lineno}")],
        )


def __stdout_writer(msg: str):
    print(msg, file=sys.stdout)


def __stderr_writer(msg: str):
    print(msg, file=sys.stderr)


__global_logger = Logger(info_writer=__stdout_writer, error_writer=__stderr_writer, debug_writer=__stdout_writer)
# log level
DEBUG = 0
INFO = 1
ERROR = 2


def set_global_logger(level: int = DEBUG):
    global __global_logger
    if level == DEBUG:
        __global_logger = Logger(
            debug_writer=__stdout_writer,
            info_writer=__stdout_writer,
            error_writer=__stderr_writer,
        )
    if level == INFO:
        __global_logger = Logger(
            info_writer=__stdout_writer,
            error_writer=__stderr_writer,
        )
    if level == ERROR:
        __global_logger = Logger(
            error_writer=__stderr_writer,
        )

now = __global_logger.now
