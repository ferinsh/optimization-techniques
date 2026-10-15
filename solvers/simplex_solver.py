
EPSILON = 1e-9

def save_tableau_snapshot(tableau, basis, num_variables, title):
    """Create a display-ready copy of the current tableau."""
    num_constraints = len(tableau) - 1
    num_slack = num_constraints

    variable_names = (
        [f"x{i + 1}" for i in range(num_variables)]
        + [f"s{i + 1}" for i in range(num_slack)]
    )

    columns = ["Basis"] + variable_names + ["RHS"]

    rows = []

    for row_index, row in enumerate(tableau[:-1]):
        basic_index = basis[row_index]
        basic_name = variable_names[basic_index]

        rows.append([basic_name] + row[:-1] + [row[-1]])

    rows.append(["Z"] + tableau[-1][:-1] + [tableau[-1][-1]])

    return {
        "title": title,
        "columns": columns,
        "rows": [row.copy() for row in rows],
    }


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


def simplex_iterations(tableau, basis, num_total, num_variables):
    """Run Simplex iterations and save every tableau."""
    iteration = 0
    max_iterations = 1000

    tableau_history = [
        save_tableau_snapshot(
            tableau, basis, num_variables, "Initial tableau"
        )
    ]

    while iteration < max_iterations:
        objective_row = tableau[-1]

        # Choose the most negative objective-row coefficient.
        entering_col = min(
            range(num_total),
            key=lambda j: objective_row[j]
        )

        # No negative coefficient means the solution is optimal.
        if objective_row[entering_col] >= -EPSILON:
            return "optimal", iteration, tableau_history

        # Minimum positive ratio test.
        candidates = []

        for i in range(len(tableau) - 1):
            coefficient = tableau[i][entering_col]

            if coefficient > EPSILON:
                ratio = tableau[i][-1] / coefficient
                candidates.append((ratio, i))

        # No eligible leaving row means the objective is unbounded.
        if not candidates:
            return "unbounded", iteration, tableau_history

        _, leaving_row = min(candidates)

        pivot_value = tableau[leaving_row][entering_col]
        leaving_variable = (
            f"x{basis[leaving_row] + 1}"
            if basis[leaving_row] < num_variables
            else f"s{basis[leaving_row] - num_variables + 1}"
        )
        entering_variable = (
            f"x{entering_col + 1}"
            if entering_col < num_variables
            else f"s{entering_col - num_variables + 1}"
        )

        pivot(tableau, leaving_row, entering_col)
        basis[leaving_row] = entering_col
        iteration += 1

        snapshot = save_tableau_snapshot(
            tableau,
            basis,
            num_variables,
            f"Iteration {iteration}",
        )
        snapshot["entering"] = entering_variable
        snapshot["leaving"] = leaving_variable
        snapshot["pivot"] = pivot_value

        tableau_history.append(snapshot)

    return "iteration_limit", iteration, tableau_history

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

    status, iterations, tableau_history = simplex_iterations(
        tableau, basis, num_total, num_variables
    )

    if status != "optimal":
        result = {
            "status": status,
            "iterations": iterations,
            "solution": None,
            "optimum": None,
            "tableau_history": tableau_history,
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
        "tableau_history": tableau_history,
    }

    # print("Status:", result["status"])
    # print("Iterations:", result["iterations"])

    # for i, value in enumerate(solution, start=1):
    #     print(f"x{i} = {value:g}")

    # print(f"Maximum Z = {optimum:g}")

    return result

def build_dual(obj_fn: list, constraints: list, sense: str = "Minimize", variable_signs=None):
    """Build the mathematical dual for an LP with explicit constraint senses.

    `constraints` use var1..varN, op, rhs. `variable_signs` may contain
    'nonnegative', 'nonpositive', or 'free' for each primal variable.
    Returns a dict describing the dual, including signs of dual variables.
    """
    sense = sense.strip().lower()
    if sense not in ("minimize", "maximize"):
        raise ValueError("sense must be 'Minimize' or 'Maximize'.")
    if not obj_fn or not constraints:
        raise ValueError("The objective and constraints must not be empty.")

    n = len(obj_fn)
    m = len(constraints)
    signs = list(variable_signs or ["nonnegative"] * n)
    if len(signs) != n:
        raise ValueError("Provide one variable sign restriction per variable.")
    valid_signs = {"nonnegative", "nonpositive", "free"}
    if any(sign not in valid_signs for sign in signs):
        raise ValueError("Variable signs must be nonnegative, nonpositive, or free.")

    dual_sense = "Maximize" if sense == "minimize" else "Minimize"
    dual_objective = [float(c["rhs"]) for c in constraints]
    dual_variable_signs = []
    for c in constraints:
        op = c.get("op")
        if op not in ("<=", ">=", "="):
            raise ValueError(f"Invalid constraint operator: {op}")
        if sense == "minimize":
            dual_variable_signs.append({">=": "nonnegative", "<=": "nonpositive", "=": "free"}[op])
        else:
            dual_variable_signs.append({"<=": "nonnegative", ">=": "nonpositive", "=": "free"}[op])

    dual_constraints = []
    for j, sign in enumerate(signs):
        coeffs = [float(c.get(f"var{j + 1}", 0)) for c in constraints]
        if sense == "minimize":
            op = {"nonnegative": "<=", "nonpositive": ">=", "free": "="}[sign]
        else:
            op = {"nonnegative": ">=", "nonpositive": "<=", "free": "="}[sign]
        dual_constraints.append({
            **{f"var{i + 1}": coeffs[i] for i in range(m)},
            "op": op,
            "rhs": float(obj_fn[j]),
        })

    steps = [
        f"Primal objective: {sense.title()} Z = " + " + ".join(f"{float(c):g}x{i + 1}" for i, c in enumerate(obj_fn)),
        f"Dual objective: {dual_sense} W = " + " + ".join(f"{float(c['rhs']):g}y{i + 1}" for i, c in enumerate(constraints)),
        "Transpose the primal constraint coefficient matrix (A becomes A^T).",
        "Assign dual-variable signs from the primal constraint directions.",
        "Assign dual constraint directions from the primal variable sign restrictions.",
    ]
    return {
        "sense": dual_sense,
        "objective": dual_objective,
        "constraints": dual_constraints,
        "variable_signs": dual_variable_signs,
        "steps": steps,
    }


def _solve_square_system(matrix, rhs):
    """Solve a square linear system with Gaussian elimination; return None if singular."""
    n = len(rhs)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        return None
    aug = [[float(v) for v in row] + [float(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < EPSILON:
            return None
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot = aug[col][col]
        aug[col] = [v / pivot for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if abs(factor) > EPSILON:
                aug[r] = [aug[r][k] - factor * aug[col][k] for k in range(n + 1)]
    return [aug[i][-1] for i in range(n)]


def recover_primal_by_complementary_slackness(obj_fn, constraints, dual_solution, dual_problem):
    """Recover a feasible primal optimum by enumerating active constraint bases.

    This is a small-LP recovery routine, not a replacement for a general LP solver.
    It currently assumes primal decision variables are nonnegative.
    """
    from itertools import combinations

    n = len(obj_fn)
    rows = []
    for i, c in enumerate(constraints, start=1):
        rows.append(([float(c.get(f"var{j + 1}", 0)) for j in range(n)], float(c["rhs"]), c["op"], f"primal constraint {i}"))
    for j in range(n):
        unit = [0.0] * n
        unit[j] = 1.0
        rows.append((unit, 0.0, ">=", f"x{j + 1} nonnegativity"))

    # Complementary-slackness equations identify active primal constraints
    # whenever their corresponding dual variable is nonzero.
    forced = []
    for i, y in enumerate(dual_solution):
        if abs(y) > 1e-7 and i < len(constraints):
            c = constraints[i]
            forced.append(([float(c.get(f"var{j + 1}", 0)) for j in range(n)], float(c["rhs"]), f"constraint {i + 1}"))

    target = float(dual_problem.get("optimum"))
    candidates = []
    for chosen in combinations(rows, n):
        matrix = [item[0] for item in chosen]
        rhs = [item[1] for item in chosen]
        x = _solve_square_system(matrix, rhs)
        if x is None or any(v < -1e-7 for v in x):
            continue
        feasible = True
        for c in constraints:
            lhs = sum(float(c.get(f"var{j + 1}", 0)) * x[j] for j in range(n))
            b, op = float(c["rhs"]), c["op"]
            if (op == "<=" and lhs > b + 1e-7) or (op == ">=" and lhs < b - 1e-7) or (op == "=" and abs(lhs - b) > 1e-7):
                feasible = False
                break
        if not feasible:
            continue

        # Complementary slackness: y_i * (b_i - A_i x) = 0.
        cs_ok = True
        for i, y_value in enumerate(dual_solution):
            if abs(y_value) <= 1e-7:
                continue
            c = constraints[i]
            lhs = sum(float(c.get(f"var{j + 1}", 0)) * x[j] for j in range(n))
            if abs(lhs - float(c["rhs"])) > 1e-6:
                cs_ok = False
                break
        if not cs_ok:
            continue

        # Complementary slackness: x_j * (A^T y - c)_j = 0 for this
        # minimization primal with nonnegative variables and a max dual.
        dual_constraints = dual_problem.get("dual_problem", {}).get("constraints", [])
        if not dual_constraints:
            dual_constraints = dual_problem.get("constraints", [])
        for j, x_value in enumerate(x):
            if abs(x_value) <= 1e-7:
                continue
            dual_constraint = dual_constraints[j]
            dual_lhs = sum(
                float(dual_constraint.get(f"var{i + 1}", 0)) * float(dual_solution[i])
                for i in range(len(dual_solution))
            )
            if abs(dual_lhs - float(dual_constraint["rhs"])) > 1e-6:
                cs_ok = False
                break
        if not cs_ok:
            continue

        z = sum(float(obj_fn[j]) * x[j] for j in range(n))
        if abs(z - target) <= 1e-6 * max(1.0, abs(target)):
            candidates.append(([0.0 if abs(v) < EPSILON else v for v in x], z, chosen))
    if not candidates:
        return None, ["Complementary slackness was applied, but no feasible primal basis matching the dual objective was found."]

    x, z, chosen = candidates[0]
    steps = ["Complementary slackness: a nonzero dual variable implies its corresponding primal constraint is binding."]
    steps.extend(f"Active equation used: {name}." for _, _, _, name in chosen)
    steps.append("Check all original constraints and non-negativity conditions.")
    steps.append(f"Primal objective Z = {z:g}; dual objective W = {target:g}.")
    steps.append("Strong duality verified within numerical tolerance." if abs(z - target) <= 1e-6 * max(1.0, abs(target)) else "Objective values do not match within tolerance.")
    return {"solution": x, "optimum": z}, steps


def min_simplex(obj_fn: list, constraints: list):
    """Minimize by solving the dual when it fits the current max-simplex backend.

    The dual converter supports all <=, >= and = primal constraints for
    nonnegative primal variables. The existing max_simplex backend has a
    narrower feasible-starting-basis requirement, so unsupported dual forms
    return a clear error rather than a misleading answer.
    """
    dual = build_dual(obj_fn, constraints, sense="Minimize")

    if any(sign != "nonnegative" for sign in dual["variable_signs"]):
        raise ValueError(
            "The dual contains nonpositive or unrestricted variables. The current Simplex backend cannot solve this form yet."
        )
    if any(c["op"] != "<=" for c in dual["constraints"]):
        raise ValueError(
            "The dual contains >= or = constraints. Use the planned Big M/Two-Phase solver for this form."
        )
    if any(c["rhs"] < -EPSILON for c in dual["constraints"]):
        raise ValueError(
            "The dual has a negative RHS and needs a solver that can construct a feasible starting basis."
        )

    result = max_simplex(dual["objective"], dual["constraints"])
    result["dual_problem"] = dual
    result["steps"] = list(dual["steps"])
    for snapshot in result.get("tableau_history", []):
        snapshot["title"] = "Dual problem — " + snapshot.get("title", "tableau")
    if result.get("status") != "optimal":
        return result

    recovered, recovery_steps = recover_primal_by_complementary_slackness(
        obj_fn, constraints, result["solution"], result
    )
    result["steps"].extend(recovery_steps)
    result["dual_solution"] = result["solution"]
    if recovered is None:
        result["status"] = "recovery_failed"
        result["solution"] = None
        result["optimum"] = None
        return result

    result["solution"] = recovered["solution"]
    result["optimum"] = recovered["optimum"]
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