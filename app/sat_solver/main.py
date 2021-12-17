from my_collection.sat_solver import parse, solve

if __name__ == "__main__":
    formula = parse(open("test.cnf", "r"))
    print(formula)
    print(solve(formula))