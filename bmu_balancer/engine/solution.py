from ortools.linear_solver.pywraplp import Solver
from pulp import LpProblem, value, LpStatus

from bmu_balancer.models.engine import Solution, Variables
from bmu_balancer.models.outputs import Instruction


def get_solution(model: LpProblem, variables: Variables) -> Solution:
    status = LpStatus[model.status]

    if status == "Optimal":
        objective = value(model.objective)

        instructions = []
        for ic, var in variables.instruction_candidates.items():
            instructions.append(Instruction(
                asset=ic.asset,
                boa=ic.boa,
                mw=var.varValue,
                start=ic.start,
                end=ic.end,
            ))

        return Solution(
            status=status,
            objective=objective,
            instructions=instructions,
        )

    else:
        return Solution(status=status)
