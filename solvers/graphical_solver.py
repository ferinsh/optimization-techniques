from itertools import combinations
import numpy as np

TOL = 1e-7

def intersect(line1, line2):
    x1, y1, r1 = line1
    x2, y2, r2 = line2

    matrix = np.array([[x1, y1], [x2, y2]], dtype=float)
    rhs = np.array([r1, r2], dtype=float)
    
    if abs(np.linalg.det(matrix)) < TOL:
        return None

    point = np.linalg.solve(matrix, rhs)
    return float(point[0]), float(point[1])

# def is_feasible(x, y, constraints):
#     if x < -TOL or y < -TOL:
#         return False

#     for c in constraints:
#         lhs =  c["a"] * x + c["b"] * y
#         rhs = c["rhs"]
#         op = c["op"]

#         if op == "<=" and lhs <= rhs + TOL:
#             return False
#         if op == ">=" and lhs >= rhs - TOL:
#             return False
#         if op == "=" and abs(lhs - rhs) > TOL:
#             return False

#         return True

def is_feasible(x, y, constraints):
    """Return True only if the point satisfies every constraint."""
    tol = 1e-7

    if x < -tol or y < -tol:
        return False

    for c in constraints:
        lhs = c["a"] * x + c["b"] * y
        rhs = c["rhs"]
        op = c["op"]

        if op == "<=" and lhs > rhs + tol:
            return False
        elif op == ">=" and lhs < rhs - tol:
            return False
        elif op == "=" and abs(lhs - rhs) > tol:
            return False

    return True

# def corner_points(constraints):
#     lines = [(c["a"], c["b"], c["rhs"]) for c in constraints]
#     lines.extend([(1.0, 0.0, 0.0), (0.0, 0.1, 0.0)])

#     points = []

#     for line1, line2 in combinations(lines, 2):
#         point = intersect(line1, line2)

#         if point is None:
#             continue

#         x, y = point
#         if is_feasible(x, y, constraints):
#             x = 0.0 if abs(x) < TOL else x
#             y = 0.0 if abs(y) < TOL else y
            
#             if not any(
#                 abs(x - px) < TOL and abs(y - py) < TOL
#                 for px, py in points
#             ):
#                 points.append((x, y))

#     return points

def corner_points(constraints):
    """Find all feasible intersections of constraint and axis lines."""
    tol = 1e-7

    lines = [
        (c["a"], c["b"], c["rhs"])
        for c in constraints
    ]

    # Non-negativity boundaries: x = 0 and y = 0.
    lines.extend([
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    ])

    points = []

    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a1, b1, r1 = lines[i]
            a2, b2, r2 = lines[j]

            det = a1 * b2 - a2 * b1

            if abs(det) < tol:
                continue

            x = (r1 * b2 - r2 * b1) / det
            y = (a1 * r2 - a2 * r1) / det

            if is_feasible(x, y, constraints):
                x = 0.0 if abs(x) < tol else x
                y = 0.0 if abs(y) < tol else y

                point = (x, y)

                if not any(
                    abs(x - px) < tol and abs(y - py) < tol
                    for px, py in points
                ):
                    points.append(point)

    return points

def is_unbounded(c1, c2, sense, constraints):
    directions = [(1.0, 0.0), (0.0, 1.0)]

    for c in constraints:
        a, b = c["a"], c["b"]
        directions.extend([(-b, a), (b, -a)])

    for dx, dy in directions:
        norm = np.hypot(dx, dy)

        if norm < TOL:
            continue

        dx, dy = dx / norm, dy / norm

        if dx < -TOL or dy < -TOL:
            continue

        valid = True

        for c in constraints:
            change = c["a"] * dx + c["b"] * dy

            if c["op"] == "<=" and change > TOL:
                valid = False
            elif c["op"] == ">=" and change < -TOL:
                valid = False
            elif c["op"] == "=" and abs(change) > TOL:
                valid = False

            if not valid:
                break

        if not valid:
            continue

        improvement = c1 * dx + c2 * dy

        if sense == "Maximize" and improvement > TOL:
            return True
        if sense == "Minimize" and improvement < -TOL:
            return True

    return False
        
def solve_lpp(c1, c2, sense, constraints):
    points = corner_points(constraints)

    if not points:
        return {
            "status": "infeasible",
            "points": [],
            "optimal_points": [],
            "optimum": None,
        }

    if is_unbounded(c1, c2, sense, constraints):
        return {
            "status": "unbounded",
            "points": points,
            "optimal_points": [],
            "optimum": None,
        }

    values = [
        c1 * x + c2 * y for x, y in points
    ]

    optimum = (
        max(values) if sense == "Maximize"
        else min(values)
    )

    best_points = [
        p for p, value in zip(points, values)
        if abs(value - optimum) < TOL * max(1.0, abs(optimum))
    ]

    return {
        "status": (
            "multiple" if len(best_points) > 1 else "optimal"
        ),
        "points": points,
        "optimal_points": best_points,
        "optimum": optimum,
    }