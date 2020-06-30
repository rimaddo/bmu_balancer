from typing import Collection, Dict

from pulp import LpBinary, LpVariable

from bmu_balancer.models.engine import Candidate, Variables


def create_variables(
        candidates: Collection[Candidate],
) -> Variables:
    """Create a set of problem variables."""
    return Variables(
        candidates=get_candidate_variables(
            candidates=candidates,
        )
    )


def get_candidate_variables(
        candidates: Collection[Candidate],
) -> Dict[Candidate, LpVariable]:
    """Create variables for the assignment of a mw value to an asset."""
    return {
        ic: LpVariable(
            name=f"var__candidate({n})",
            cat=LpBinary,
        )
        for n, ic in enumerate(candidates)
    }
