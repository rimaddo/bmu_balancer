import logging

from pulp import LpProblem, LpStatus, value

from bmu_balancer.models.engine import Solution, Variables
from bmu_balancer.models.outputs import Instruction

log = logging.getLogger(__name__)


def get_solution(model: LpProblem, variables: Variables) -> Solution:
    status = LpStatus[model.status]

    if status == "Optimal":
        objective = value(model.objective)

        instructions = []
        for assignment, var in variables.assignments.items():
            if var.varValue > 0:
                for candidate in assignment.candidates:
                    instructions.append(Instruction(
                        asset=candidate.asset,
                        boa=candidate.boa,
                        mw=candidate.mw,
                        start=candidate.start,
                        end=candidate.end,
                    ))

        log.info(f"Got {len(instructions)} instructions choices.")

        return Solution(
            status=status,
            objective=objective,
            instructions=instructions,
        )

    else:
        return Solution(status=status)
