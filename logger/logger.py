from __future__ import annotations

import inspect
import sys
import time
from typing import Any, Callable, List, Tuple

Writer = Callable[[str, ], None]


def stdout_writer(msg: str):
    print(msg, file=sys.stdout, end="")


def stderr_writer(msg: str):
    print(msg, file=sys.stderr, end="")


class Context:
    __info_writer: Writer
    __error_writer: Writer
    __now: time.struct_time
    __kv_list: List[Tuple[str, Any]]

    def __init__(self, info_writer: Writer, error_writer: Writer, now: time.struct_time,
                 kv_list: List[Tuple[str, Any]]):
        self.__info_writer = info_writer
        self.__error_writer = error_writer
        self.__now = now
        self.__kv_list = kv_list

    def info(self, msg: str):
        self.__info_writer(self.__to_log(msg))

    def error(self, msg: str):
        self.__error_writer(self.__to_log(msg))

    def with_field(self, key: str, val: Any) -> Context:
        return Context(
            info_writer=self.__info_writer,
            error_writer=self.__error_writer,
            now=self.__now,
            kv_list=[*self.__kv_list, (key, val)],
        )

    def __to_log(self, msg: str) -> str:
        time_str = time.strftime('%Y/%m/%d %H:%M:%S', self.__now)
        field_str_list = [f"{key}={val}" for key, val in self.__kv_list]
        if not msg.endswith("\n"):
            msg += "\n"
        return "|".join([time_str, *field_str_list, msg])


class Logger:
    __info_writer: Writer
    __error_writer: Writer

    def __init__(self, info_writer: Writer = stdout_writer, error_writer: Writer = stderr_writer):
        self.__info_writer = info_writer
        self.__error_writer = error_writer

    def now(self) -> Context:
        caller_frame: inspect.FrameInfo = inspect.getouterframes(inspect.currentframe(), 0)[1]
        return Context(
            info_writer=self.__info_writer,
            error_writer=self.__error_writer,
            now=time.localtime(),
            kv_list=[("caller", f"{caller_frame.filename}:{caller_frame.lineno}")],
        )
