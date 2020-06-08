from typing import List

from bmu_balancer.models.engine import InstructionCandidate
from bmu_balancer.models.inputs import AssetState, BOA
from bmu_balancer.models.outputs import Instruction
from bmu_balancer.operations.instruction_helpers import get_prior_instruction
from bmu_balancer.operations.key_store import KeyStore
from bmu_balancer.operations.pre_solve.check_instruction_is_valid import (
    asset_can_be_assigned_to_boa,
)
from bmu_balancer.operations.pre_solve.get_adjusted_times import get_adjusted_end, get_adjusted_start
from bmu_balancer.operations.pre_solve.get_mw_bounds import get_mw_options
from bmu_balancer.operations.utils import get_item_at_time


def generate_instruction_candidates(
        boa: BOA,
        states: KeyStore[AssetState],
        instructions: KeyStore[Instruction],
) -> List[InstructionCandidate]:
    """Generate a set of valid instruction candidate
    variables given a boa and the asset states."""

    candidates = []
    for asset in boa.assets:

        # Identify if instructions are in/progress
        # and which if any have most recently finished.
        current_instruction = get_item_at_time(
            items=instructions,
            asset=asset,
            time=boa.start,
        )
        prior_instruction = get_prior_instruction(
            asset=asset,
            instructions=instructions,
            time=boa.start,
        )

        if asset_can_be_assigned_to_boa(
            asset=asset,
            boa=boa,
            states=states,
            current_instruction=current_instruction,
            prior_instruction=prior_instruction,
        ):
            # Given a valid asset that can be assigned to the boa
            # for a non-zero time.

            # Define candidate parameters
            adjusted_start = get_adjusted_start(
                asset=asset,
                boa=boa,
                current_instruction=current_instruction,
            )
            adjusted_end = get_adjusted_end(
                asset=asset,
                boa=boa,
                current_instruction=current_instruction,
                adjusted_start=adjusted_start,
            )

            mw_options = get_mw_options(
                asset=asset,
                boa=boa,
                states=states,
                current_instruction=current_instruction,
            )
            for mw in mw_options:
                # Add new candidate
                candidates.append(
                    InstructionCandidate(
                        asset=asset,
                        boa=boa,
                        adjusted_start=adjusted_start,
                        adjusted_end=adjusted_end,
                        mw=mw,
                    )
                )
    return candidates
