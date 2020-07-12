from collections import defaultdict

from pulp import LpProblem

from bmu_balancer.models.engine import Variables
from bmu_balancer.models.inputs import BOA


def add_constraints(model: LpProblem, variables: Variables, boa: BOA) -> None:
    # asset_to_ics = defaultdict(list)

    # Minimum profit a customer has to make to run an asset
    for assignment, var in variables.assignments.items():
        for candidate in assignment.candidates:
            if candidate.mw != 0:
                model += (
                    var * boa.price_mw_hr * candidate.hours
                    >=
                    candidate.asset.min_required_profit * var
                )
            # asset_to_ics[candidate.asset].append(candidate)

    # Asset can only be assigned once
    model += (
        sum(
            var
            for var in variables.assignments.values()
        ) == 1
    )

    # # Asset can only be assigned once
    # for asset, candidates in asset_to_ics.items():
    #     model += (
    #         sum(
    #             variables.candidates[candidate]
    #             for candidate in candidates
    #         ) == 1
    #     )

    # Total value is less than boa
    for assignment, var in variables.assignments.items():
        model += sum(
            var * candidate.mw
            for candidate in assignment.candidates
        ) <= boa.mw
