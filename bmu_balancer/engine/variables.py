from typing import Collection, Dict

from pulp import LpBinary, LpVariable

from bmu_balancer.models.engine import Assignment, Variables


def create_variables(
        assignments: Collection[Assignment],
) -> Variables:
    """Create a set of problem variables."""
    return Variables(
        assignments=get_candidate_variables(
            assignments=assignments,
        )
    )


def get_candidate_variables(
        assignments: Collection[Assignment],
) -> Dict[Assignment, LpVariable]:
    """Create variables for the assignment of a mw value to an asset."""
    return {
        assignment: LpVariable(
            name=f"var__candidate({n})",
            cat=LpBinary,
        )
        for n, assignment in enumerate(assignments)
    }
