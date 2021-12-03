# sparsest-solution-underdetermined-linear-system

optimize norm with underdetermined system equality constraint

## problem statement

```
Problem 1:
Minimize ||x||_p
such that
    Ax=b
where
    x \in R^n
    A \in R^{m \times n}
    b \in R^m
    p \in R_+
```

## algorithm

### unconstrained optimization (L_p norm, p >= 1)

```
Problem 2:
Minimize ||Ax-b||_2^2 + ||x||_p^p
```

### linear programming (L_1 norm)

```
------------------------------------------------
Problem 3:
Minimize 1^T y (sum of all elements of y)
such that
    y >= |x|
    Ax = b
where y \in R^n
------------------------------------------------
Claim 1:
    If Problem 1 (with p=1) has a solution, then Problem 3 has the same solution.
------------------------------------------------
Claim 2:
    Problem 3 can be formulated as a linear program with a variable u = [x, y] \in R^{2n}
------------------------------------------------
```
