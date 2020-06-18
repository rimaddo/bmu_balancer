from typing import Dict, List

from pulp import LpVariable

from bmu_balancer.models.engine import Variables, InstructionCandidate


def create_variables(
        instruction_candidates: List[InstructionCandidate],
) -> Variables:
    """Create a set of problem variables."""
    return Variables(
        instruction_candidates=get_instruction_candidate_variables(
            instruction_candidates=instruction_candidates,
        )
    )


def get_instruction_candidate_variables(
        instruction_candidates: List[InstructionCandidate],
) -> Dict[InstructionCandidate, LpVariable]:
    """Create variables for the assignment of a mw value to an asset."""
    return {
        ic: LpVariable(
            name=f"var__instruction_candidate({n})",
            lowBound=ic.min_mw,
            upBound=ic.max_mw,
        )
        for n, ic in enumerate(instruction_candidates)
    }
