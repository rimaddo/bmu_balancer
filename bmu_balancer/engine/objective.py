from pulp import LpProblem

from bmu_balancer.models import BOA, Rate
from bmu_balancer.models.engine import Variables
from bmu_balancer.operations.instruction_helpers import get_instruction_cost
from bmu_balancer.operations.key_store import KeyStore


def set_objective(model: LpProblem, variables: Variables, boa: BOA, rates: KeyStore[Rate]) -> None:
    model += sum(
        var * (
            # Profit
            boa.price_mw_hr * candidate.hours * candidate.mw
            # Cost
            - get_instruction_cost(instruction=candidate, rates=rates)
        )
        for candidate, var in variables.candidates.items()
    )
