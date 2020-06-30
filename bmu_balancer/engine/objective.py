from pulp import LpProblem

from bmu_balancer.models import BOA
from bmu_balancer.models.engine import Variables
from bmu_balancer.operations.instruction_helpers import get_instruction_cost


def set_objective(model: LpProblem, variables: Variables, boa: BOA) -> None:
    model += sum(
        var * (
            # Profit
            boa.price_mw_hr * candidate.hours * candidate.mw
            # Cost
            - get_instruction_cost(instruction=candidate)

            # Penalise for imbalance over
            # Penalise for imbalance under
        )
        for candidate, var in variables.candidates.items()
    )
