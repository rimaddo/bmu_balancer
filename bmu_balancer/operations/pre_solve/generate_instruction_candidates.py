import logging
import sys
from datetime import datetime
from time import time
from typing import List

from bmu_balancer.models.engine import Candidate
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

log = logging.getLogger(__name__)

NOW = datetime.utcnow()


def generate_instruction_candidates(
        boa: BOA,
        states: KeyStore[AssetState],
        instructions: KeyStore[Instruction],
        execution_time: datetime = NOW,
) -> List[Candidate]:
    """Generate a set of valid instruction candidate
    variables given a boa and the asset states."""
    log.info("Generating instruction candidates...")
    start = time()

    candidates = []
    for asset in boa.assets:

        # Identify if instructions are in/progress
        # and which if any have most recently finished.
        current_instruction = get_item_at_time(
            items=instructions,
            asset=asset,
            time=boa.start,
            nullable=True,
        )
        prior_instruction = get_prior_instruction(
            asset=asset,
            instructions=instructions,
            time=boa.start,
        )

        valid = asset_can_be_assigned_to_boa(
            asset=asset,
            boa=boa,
            states=states,
            current_instruction=current_instruction,
            prior_instruction=prior_instruction,
        )
        if valid:
            # Given a valid asset that can be assigned to the boa
            # for a non-zero time.

            # Define candidate parameters
            adjusted_start = get_adjusted_start(
                asset=asset,
                boa=boa,
                current_instruction=current_instruction,
                execution_time=execution_time,
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
                adjusted_start=adjusted_start,
                adjusted_end=adjusted_end,
            )

            asset_candidates = [
                Candidate(
                    asset=asset,
                    boa=boa,
                    adjusted_start=adjusted_start,
                    adjusted_end=adjusted_end,
                    mw=mw,
                )
                for mw in mw_options
                if abs(mw) <= asset.capacity
            ]
            log.info(f"Added {len(asset_candidates)} candidates for {asset}.")

            candidates.extend(asset_candidates)

    log.info(f"Finished generating candidates, got {len(candidates)}. Took: {round(time() - start, 4)} secs")
    return candidates
