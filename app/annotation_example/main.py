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

    def parse(self, o: dict[str, Any]) -> Record:
        for field_name, field_value in o.items():
            setattr(self, field_name, field_value)
        return self


def to_dataframe(*records: Record) -> pd.DataFrame:
    assert len(records) > 0, "records must not be empty"
    return pd.DataFrame(
        data=map(lambda record: tuple(zip(*tuple(record)))[1], records),
        columns=records[0].__annotations__.keys(),
    )


def from_dataframe(df: pd.DataFrame) -> Iterable[dict[str, Any]]:
    return map(lambda row: dict(row[1]), df.iterrows())


class MyRecord(Record):
    id: int
    name: str
    data: object


if __name__ == "__main__":
    r = MyRecord(id=3, name="1", data=None)
    print(tuple(r))
    print(dict(r))
    df = to_dataframe(
        MyRecord(1, name="2", data=None),
        MyRecord(2, id=3, name="4", data=None)
    )
    print(df)
    data = map(lambda kwargs: MyRecord(**kwargs), from_dataframe(df))
    print(list(map(dict, data)))
