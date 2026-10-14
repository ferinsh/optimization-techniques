
EPSILON = 1e-9


def check_negativity(constraints: list[dict]) -> list[dict]:
    """Make every RHS non-negative, reversing inequalities when needed."""
    normalized = []

    for constraint in constraints:
        c = constraint.copy()

        if c["op"] not in ("<=", ">=", "="):
            raise ValueError(f"Invalid constraint operator: {c['op']}")

        if c["rhs"] < 0:
            for key in c:
                if key not in ("op", "rhs"):
                    c[key] = -c[key]

            c["rhs"] = -c["rhs"]

            if c["op"] == "<=":
                c["op"] = ">="
            elif c["op"] == ">=":
                c["op"] = "<="

        normalized.append(c)

    return normalized


def convert_to_equations(
    constraints: list[dict],
    num_variables: int
) -> list[list[float]]:
    """
    Convert <= constraints into equations by adding slack variables.

    Returns each equation as:
        [variable coefficients, slack coefficients, RHS]
    """
    num_constraints = len(constraints)
    equations = []

    for i, constraint in enumerate(constraints):
        if constraint["op"] != "<=":
            raise ValueError(
                "This Simplex implementation supports <= constraints "
                "after normalization. Constraints requiring surplus or "
                "artificial variables need the Big M or Two-Phase method."
            )

        row = []

        for j in range(num_variables):
            key = f"var{j + 1}"
            row.append(float(constraint.get(key, 0)))

        # Add one slack variable for this constraint.
        for j in range(num_constraints):
            row.append(1.0 if i == j else 0.0)

        row.append(float(constraint["rhs"]))
        equations.append(row)

    return equations


def read_lpp(obj_fn: list, constraints: list):
    """Validate the input and construct the initial simplex tableau."""
    if not obj_fn:
        raise ValueError("The objective function needs at least one variable.")

    if not constraints:
        raise ValueError("Add at least one constraint.")

    if any(not isinstance(v, (int, float)) for v in obj_fn):
        raise ValueError("Objective coefficients must be numbers.")

    num_variables = len(obj_fn)

    for i, c in enumerate(constraints, start=1):
        if "rhs" not in c or "op" not in c:
            raise ValueError(f"Constraint {i} needs 'op' and 'rhs'.")

        if not isinstance(c["rhs"], (int, float)):
            raise ValueError(f"Constraint {i}: RHS must be numeric.")

        for j in range(num_variables):
            key = f"var{j + 1}"
            value = c.get(key, 0)

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Constraint {i}: {key} must be numeric."
                )

    constraints = check_negativity(constraints)

    equations = convert_to_equations(
        constraints, num_variables
    )

    num_slack = len(constraints)
    num_total = num_variables + num_slack

    # Objective row: -c1, -c2, ..., 0, 0, ...
    objective_row = (
        [-float(c) for c in obj_fn]
        + [0.0] * num_slack
        + [0.0]
    )

    tableau = equations + [objective_row]

    # Initially, each slack variable is basic.
    basis = [
        num_variables + i for i in range(num_slack)
    ]

    return tableau, basis, num_variables, num_total


def pivot(tableau, pivot_row, pivot_col):
    """Perform a Gauss-Jordan pivot operation."""
    pivot_value = tableau[pivot_row][pivot_col]

    if abs(pivot_value) < EPSILON:
        raise ArithmeticError("Cannot pivot on a zero value.")

    tableau[pivot_row] = [
        value / pivot_value
        for value in tableau[pivot_row]
    ]

    pivot_width = len(tableau[pivot_row])

    for i in range(len(tableau)):
        if i == pivot_row:
            continue

        factor = tableau[i][pivot_col]

        if abs(factor) < EPSILON:
            continue

        tableau[i] = [
            tableau[i][j] - factor * tableau[pivot_row][j]
            for j in range(pivot_width)
        ]


def simplex_iterations(tableau, basis, num_total):

    """Run primal Simplex iterations until optimal or unbounded."""
    iteration = 0
    max_iterations = 1000

    while iteration < max_iterations:
        
        iteration += 1
        print(f"iteration {iteration}")
        for row in tableau:
            print(row)

        objective_row = tableau[-1]

        # Choose the most negative objective-row coefficient.
        entering_col = min(
            range(num_total),
            key=lambda j: objective_row[j]
        )

        # No negative coefficient means the solution is optimal.
        if objective_row[entering_col] >= -EPSILON:
            return "optimal", iteration

        # Minimum positive ratio test.
        candidates = []

        for i in range(len(tableau) - 1):
            coefficient = tableau[i][entering_col]

            if coefficient > EPSILON:
                ratio = tableau[i][-1] / coefficient
                candidates.append((ratio, i))

        # No eligible leaving row means the objective is unbounded.
        if not candidates:
            return "unbounded", iteration

        _, leaving_row = min(candidates)

        pivot(tableau, leaving_row, entering_col)
        basis[leaving_row] = entering_col

    return "iteration_limit", iteration


def max_simplex(obj_fn: list, constraints: list):
    """
    Maximize Z = c1*x1 + c2*x2 + ...

    Assumes all decision variables are non-negative.
    Supports <= constraints that produce a feasible initial
    slack-variable basis after RHS normalization.
    """
    tableau, basis, num_variables, num_total = read_lpp(
        obj_fn, constraints
    )

    status, iterations = simplex_iterations(
        tableau, basis, num_total
    )

    if status != "optimal":
        result = {
            "status": status,
            "iterations": iterations,
            "solution": None,
            "optimum": None,
        }
        print(result)
        return result

    # Non-basic variables are zero; basic variables equal RHS.
    solution = [0.0] * num_variables

    for row_index, basic_variable in enumerate(basis):
        if basic_variable < num_variables:
            solution[basic_variable] = tableau[row_index][-1]

    # The objective row's RHS is the maximum objective value.
    optimum = tableau[-1][-1]

    # Remove tiny floating-point errors.
    solution = [
        0.0 if abs(value) < EPSILON else value
        for value in solution
    ]

    if abs(optimum) < EPSILON:
        optimum = 0.0

    result = {
        "status": "optimal",
        "iterations": iterations,
        "solution": solution,
        "optimum": optimum,
    }

    print("Status:", result["status"])
    print("Iterations:", result["iterations"])

    for i, value in enumerate(solution, start=1):
        print(f"x{i} = {value:g}")

    print(f"Maximum Z = {optimum:g}")

    return result


if __name__ == "__main__":
    # Maximize Z = 3x1 + 5x2
    #
    # Subject to:
    # x1       <= 4
    #      2x2 <= 12
    # 3x1 + 2x2 <= 18
    # x1, x2 >= 0

    max_simplex(
        [3, 5],
        [
            {"var1": 1, "var2": 0, "op": "<=", "rhs": 4},
            {"var1": 0, "var2": 2, "op": "<=", "rhs": 12},
            {"var1": 3, "var2": 2, "op": "<=", "rhs": 18},
        ]
    )
