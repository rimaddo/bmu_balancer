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
        for candidate, var in variables.candidates.items():
            if var.varValue > 0:
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
