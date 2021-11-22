from __future__ import annotations

import inspect
import time
from typing import Any, Callable

Writer = Callable[[str, ], None]


def print_writer(msg: str):
    print(msg)


class Context:
    __info_writer: Writer
    __error_writer: Writer
    __now: time.struct_time
    __kv_list: list[tuple[str, Any]]

    def __init__(self, info_writer: Writer, error_writer: Writer, now: time.struct_time,
                 kv_list: list[tuple[str, Any]]):
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
        return "|".join([time_str, *field_str_list, msg])


class Logger:
    __info_writer: Writer
    __error_writer: Writer

    def __init__(self, info_writer: Writer = print_writer, error_writer: Writer = print_writer):
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


if __name__ == "__main__":
    logger = Logger()
    logger.now().info("hello")
    logger.now().with_field("key", "val").error("with field")
