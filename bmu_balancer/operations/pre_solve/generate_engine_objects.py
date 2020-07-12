import logging
from datetime import datetime, timedelta
from itertools import product
from time import time
from typing import Dict, List, Iterator, Optional

from bmu_balancer.models.engine import Assignment, Candidate
from bmu_balancer.models.inputs import Asset, BOA, State
from bmu_balancer.models.outputs import Instruction
from bmu_balancer.operations.instruction_helpers import get_prior_instruction
from bmu_balancer.operations.key_store import KeyStore
from bmu_balancer.operations.pre_solve.check_instruction_is_valid import (
    asset_can_be_assigned_to_boa,
)
from bmu_balancer.operations.pre_solve.get_adjusted_times import get_adjusted_end, get_adjusted_start
from bmu_balancer.operations.pre_solve.get_mw_bounds import get_mw_options
from bmu_balancer.operations.ramp_helpers import get_ramp_down_end_time, get_ramp_up_start_time
from bmu_balancer.operations.utils import get_item_at_time

log = logging.getLogger(__name__)

NOW = datetime.utcnow()


def generate_assignment_candidates(
        candidates: Dict[Asset, List[Candidate]],
) -> Iterator[Assignment]:
    start = time()

    combinations = list(product(*candidates.values()))

    assignments = [
        Assignment(candidates=combination)
        for combination in combinations
    ]
    log.info(f"Finished generating assignments, got {len(assignments)}. Took: {round(time() - start, 4)} secs")
    return assignments

    # for combination in combinations:
    #     total_mw = sum(c.mw for c in combination)
    #     if total_mw == boa.mw:
    #     yield Assignment(candidates=combination)


def generate_instruction_candidates(
        boa: BOA,
        states: KeyStore[State],
        instructions: KeyStore[Instruction],
        execution_time: datetime = NOW,
) -> Dict[Asset, List[Candidate]]:
    """Generate a set of valid instruction candidate
    variables given a boa and the asset states."""
    log.info("Generating instruction candidates...")
    start = time()

    candidates = {}
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
            # TODO: We can do more interesting things with the start / end given BOA rates
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
                    adjusted_start=get_start_for_boa_mw(mw=mw, boa=boa),
                    adjusted_end=get_end_for_boa_mw(mw=mw, boa=boa),
                    mw=mw,
                )
                for mw in mw_options
                if abs(mw) <= asset.capacity
            ]
            log.info(f"Added {len(asset_candidates)} candidates for {asset}.")

            candidates[asset] = asset_candidates

    log.info(f"Finished generating candidates, got {len(candidates)}. Took: {round(time() - start, 4)} secs")
    return candidates


def get_start_for_boa_mw(mw: float, boa: BOA):
    # How long will it take to get to the lower mw?
    time_to_get_to_mw = get_ramp_up_start_time(rates=boa.rates, mw=mw)
    start = boa.ramp_start + timedelta(hours=time_to_get_to_mw)
    return start


def get_end_for_boa_mw(mw: float, boa: BOA):
    time_to_get_to_mw = get_ramp_down_end_time(rates=boa.rates, mw=mw)
    end = boa.ramp_end - timedelta(hours=time_to_get_to_mw)
    return end
