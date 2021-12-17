from __future__ import annotations

import inspect
from typing import List, Union, Callable, Tuple

from my_collection import model


class Symbol(str):
    def __repr__(self) -> str:
        return f"{self}"


class Function(model.Record):
    param: List[Symbol]
    expr: Expression

    def __repr__(self) -> str:
        return ".".join([f"λ{p}" for p in self.param]) + "." + self.expr.__repr__()

    def encode(self, from_count: int = 0) -> Tuple[Function, int]:
        to_count = from_count + len(self.param)
        param = [Symbol(f"x_{i}") for i in range(len(self.param))]
        expr = self.expr
        for i, p in enumerate(param):
            expr = expr.substitute(self.param[i], p)
        return Function(param=param, expr=expr), to_count

    def __eq__(self, other: Function) -> bool:
        if len(self.param) != len(other.param):
            return False

        return self.encode()[0].expr == other.encode()[0].expr


# list of Symbol, Function, Expression
# Expression = List[Union[Symbol, Function, List]]

class Expression(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def encode(self, from_count: int = 0) -> Tuple[Expression, int]:
        # rename symbols
        to_count = from_count
        out = []
        for i, e in enumerate(self):
            encoded = e
            if isinstance(encoded, Function) or isinstance(e, Expression):
                encoded, d_count = encoded.encode(to_count)
                to_count += d_count
            out.append(encoded)
        return Expression(out), to_count

    def __eq__(self, other: Expression) -> bool:
        e1 = self.reduce()
        e2 = other.reduce()
        if len(e1) != len(e2):
            return False
        for i1, i2 in zip(e1, e2):
            if i1 != i2:
                return False
        return True

    def reduce(self) -> Expression:
        global count
        e, count = self.encode(count)
        # e is list
        if len(e) == 0:
            return e
        # len(e) >= 1
        if isinstance(e[0], Symbol):
            return e
        if isinstance(e[0], Function):
            if len(e[0].param) == 0:
                return Expression([*e[0].expr, *e[1:]]).reduce()
            if len(e) == 1:
                return e
            # len(e) >= 2
            # print(f"apply {e[1]} into {e[0]}")
            return Expression([
                Function(param=e[0].param[1:], expr=e[0].expr.substitute(e[0].param[0], e[1]).reduce()),
                *e[2:]],
            ).reduce()

        if isinstance(e[0], List):  # List
            if len(e) == 1:
                return Expression(e[0]).reduce()
            # len(e) >= 2
            if len(e[0]) == 0:
                return Expression(e[1:]).reduce()
            # len(e[0]) >= 1
            o = Expression(e[0]).reduce()
            if len(o) == 0:
                return Expression(e[1:]).reduce()
            # len(o) >= 1
            return Expression([*o, *e[1:]]).reduce()

    def substitute(self, s: Symbol, a: Union[Symbol, Function, Expression]) -> Expression:
        o = []
        for ee in self:
            if isinstance(ee, Symbol):
                o.append(a if ee == s else ee)
            if isinstance(ee, Function):
                o.append(Function(param=ee.param, expr=ee.expr.substitute(s, a)))
            if isinstance(ee, Expression):
                o.append(ee.substitute(s, a))
        return Expression(o)


count = 0


def new_lambda(l: Callable[[Symbol, ...], List]) -> Function:
    num_params = len(inspect.getfullargspec(l).args)
    global count
    param = [Symbol(f"x_{count + i}") for i in range(num_params)]
    count += num_params
    return Function(param=param, expr=Expression(l(*param)))


if __name__ == "__main__":
    FALSE = new_lambda(lambda x, y: [y])
    TRUE = new_lambda(lambda x, y: [x])
    AND = new_lambda(lambda p, q: [p, q, p])
    OR = new_lambda(lambda p, q: [p, p, q])
    NOT = new_lambda(lambda p, a, b: [p, b, a])
    if __debug__:
        print("debugging")

    assert Expression([NOT, TRUE]).reduce()[0] == FALSE
    assert Expression([NOT, FALSE]).reduce()[0] == TRUE
    assert Expression([AND, FALSE, FALSE]).reduce()[0] == FALSE
    assert Expression([AND, FALSE, TRUE]).reduce()[0] == FALSE
    assert Expression([AND, TRUE, FALSE]).reduce()[0] == FALSE
    assert Expression([AND, TRUE, TRUE]).reduce()[0] == TRUE
    assert Expression([OR, FALSE, FALSE]).reduce()[0] == FALSE
    assert Expression([OR, FALSE, TRUE]).reduce()[0] == TRUE
    assert Expression([OR, TRUE, FALSE]).reduce()[0] == TRUE
    assert Expression([OR, TRUE, TRUE]).reduce()[0] == TRUE

    ZERO = new_lambda(lambda f, x: x)
    SUCC = new_lambda(lambda n, f, x: [f, [n, f, x]])

    numbers = [ZERO]
    for i in range(1, 10):
        numbers.append(Expression([SUCC, numbers[-1]]).reduce())

    for i, number in enumerate(numbers):
        print(i, number.encode())

    print("no error found")
