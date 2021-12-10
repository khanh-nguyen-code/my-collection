from __future__ import annotations

from typing import List, Any, Union, Callable

import pydantic

from my_collection import model


class Symbol(str):
    def __repr__(self) -> str:
        return f"{self}"


class Function(model.Record):
    param: List[Symbol]
    expr: Expression

    def __repr__(self) -> str:
        return ".".join([f"λ{p}" for p in self.param]) + "." + self.expr.__repr__()


# list of Symbol, Function, Expression
Expression = List[Union[Symbol, Function, List]]


def reduce(e: Expression) -> Expression:
    # e is list
    if len(e) == 0:
        return e
    # len(e) >= 1
    if isinstance(e[0], Symbol):
        return e
    if isinstance(e[0], Function):
        if len(e[0].param) == 0:
            return reduce([*e[0].expr, *e[1:]])
        if len(e) == 1:
            return e
        # len(e) >= 2
        print(f"apply {e[1]} into {e[0]}")
        return reduce([Function(param=e[0].param[1:], expr=__substitute(e[0].expr, e[0].param[0], e[1])), *e[2:]])

    if isinstance(e[0], List):  # List
        if len(e) == 1:
            return reduce(e[0])
        # len(e) >= 2
        if len(e[0]) == 0:
            return reduce(e[1:])
        # len(e[0]) >= 1
        o = reduce(e[0])
        if len(o) == 0:
            return reduce(e[1:])
        # len(o) >= 1
        return reduce([*o, *e[1:]])


def __substitute(e: Expression, s: Symbol, a: Expression) -> Expression:
    # e is List
    o = []
    for ee in e:
        if isinstance(ee, Symbol):
            o.append(a if ee == s else ee)
        if isinstance(ee, Function):
            o.append(Function(param=ee.param, expr=__substitute(ee.expr, s, a)))
        if isinstance(ee, List):  # List
            o.append(__substitute(ee, s, a))
    return o


count = 0


def new_function(num_params: int, expr: Callable[[Symbol, ...], Expression]) -> Function:
    global count
    param = [Symbol(f"x_{count + i}") for i in range(num_params)]
    count += num_params
    return Function(param=param, expr=expr(*param))


if __name__ == "__main__":
    FALSE = new_function(2, lambda x, y: [y])
    TRUE = new_function(2, lambda x, y: [x])
    NOT = new_function(1, lambda b: [b, FALSE, TRUE])
    print(reduce([NOT, TRUE])[0])
