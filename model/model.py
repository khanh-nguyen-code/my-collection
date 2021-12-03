from __future__ import annotations

from typing import Iterable, Any

import pandas as pd


class Record:
    def __init__(self, *args, **kwargs):
        # set args
        for field_name, field_value in zip(self.__annotations__.keys(), args):
            setattr(self, field_name, field_value)
        # set kwargs
        for field_name, field_value in kwargs.items():
            setattr(self, field_name, field_value)

    def __iter__(self):
        for field_name in self.__annotations__.keys():
            yield field_name, getattr(self, field_name)


def to_dataframe(*records: Record) -> pd.DataFrame:
    assert len(records) > 0, "records must not be empty"
    return pd.DataFrame(
        data=map(lambda record: tuple(zip(*tuple(record)))[1], records),
        columns=records[0].__annotations__.keys(),
    )


def from_dataframe(df: pd.DataFrame) -> Iterable[dict[str, Any]]:
    return map(lambda row: dict(row[1]), df.iterrows())
