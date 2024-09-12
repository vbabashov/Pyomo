# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

from ortools.sat.python import cp_model


def solve_with_time_limit_sample_sat():
    """Minimal CP-SAT example to showcase calling the solver."""
    # Creates the model.
    model = cp_model.CpModel()
    # Creates the variables.
    num_vals = 3
    x = model.new_int_var(0, num_vals - 1, "x")
    y = model.new_int_var(0, num_vals - 1, "y")
    z = model.new_int_var(0, num_vals - 1, "z")
    # Adds an all-different constraint.
    model.add(x != y)

    # Creates a solver and solves the model.
    solver = cp_model.CpSolver()

    # Sets a time limit of 10 seconds.
    solver.parameters.max_time_in_seconds = 10.0

    status = solver.solve(model)

    if status == cp_model.OPTIMAL:
        print(f"x = {solver.value(x)}")
        print(f"y = {solver.value(y)}")
        print(f"z = {solver.value(z)}")
    else:
        print (status)
    


solve_with_time_limit_sample_sat()
# [END program]