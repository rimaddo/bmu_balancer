from pulp import LpProblem

from bmu_balancer.models.engine import Variables
from bmu_balancer.models.inputs import Offer, BOA


def add_constraints(model: LpProblem, variables: Variables, boa: BOA) -> None:

    # Minimum profit a customer has to make to run an asset
    for ic, var in variables.instruction_candidates.items():
        model += (
            var * boa.price_mw_hr * ic.hours
            >=
            ic.asset.min_required_profit * var
        )

    # Total value is less than boa
    model += sum(
        var
        for var in variables.instruction_candidates.values()
    ) <= boa.mw
