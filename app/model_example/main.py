from __future__ import annotations

import model


class MyRecord(model.Record):
    id: int
    name: str
    data: object


if __name__ == "__main__":
    r = MyRecord(id=3, name="1", data=None)
    print(tuple(r))
    print(dict(r))
    df = model.to_dataframe(
        MyRecord(1, name="2", data=None),
        MyRecord(2, id=3, name="4", data=None)
    )
    print(df)
    data = map(lambda kwargs: MyRecord(**kwargs), model.from_dataframe(df))
    print(list(map(dict, data)))
