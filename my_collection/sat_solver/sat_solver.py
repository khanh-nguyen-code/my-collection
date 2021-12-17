import io
from typing import Tuple, Optional, TextIO

from pvectorc import PVector
from pyrsistent import v, pvector

Literal = int
Formula = PVector  # PVector of PVector of Literals
Assignment = PVector  # PVector of Literals

ScanResult = Optional[int]
SCAN_EMPTY_CLAUSE = None
SCAN_NOTHING = 0


def __scan_formula(formula: Formula) -> ScanResult:
    clause: PVector
    for clause in formula:
        if len(clause) == 0:
            return SCAN_EMPTY_CLAUSE
        if len(clause) == 1:
            return clause[0]
    return SCAN_NOTHING


def __substitute(formula: Formula, literal: Literal) -> Formula:
    if len(formula) == 0:
        return formula
    new_formula = pvector()
    clause: PVector
    for clause in formula:
        if literal in clause:
            continue
        for i in range(len(clause)):
            if -literal == clause[i]:
                clause = clause.set(i, clause[-1])[:-1]
                break
        new_formula = new_formula.append(clause)
    return new_formula


def solve(formula: Formula, canvas: Assignment = pvector()) -> Tuple[bool, Optional[Assignment]]:
    if len(formula) == 0:
        return True, canvas
    scan_result = __scan_formula(formula)
    if scan_result == SCAN_EMPTY_CLAUSE:
        return False, None
    if scan_result == SCAN_NOTHING:
        guess = formula[0][0]
        b1, l1 = solve(__substitute(formula, guess), canvas.append(guess))
        if b1:
            return True, l1
        b2, l2 = solve(__substitute(formula, -guess), canvas.append(-guess))
        if b2:
            return True, l2
        return False, None
    # unit
    return solve(__substitute(formula, scan_result), canvas.append(scan_result))


def parse(r: TextIO) -> Formula:
    in_data = r.readlines()

    cnf = list()
    cnf.append(list())

    for line in in_data:
        tokens = line.split()
        if len(tokens) != 0 and tokens[0] not in ("p", "c"):
            for tok in tokens:
                lit = int(tok)
                if lit == 0:
                    cnf.append(list())
                else:
                    cnf[-1].append(lit)

    assert len(cnf[-1]) == 0
    cnf.pop()
    return pvector([pvector(clause) for clause in cnf])



