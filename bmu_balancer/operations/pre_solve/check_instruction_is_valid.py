import logging
from datetime import timedelta

from bmu_balancer.models import Asset, AssetState, BOA, Instruction
from bmu_balancer.operations.key_store import KeyStore
from bmu_balancer.operations.utils import get_items_for_period

log = logging.getLogger(__name__)


def asset_can_be_assigned_to_boa(
        asset: Asset,
        boa: BOA,
        states: KeyStore[AssetState],
        current_instruction: Instruction,
        prior_instruction: Instruction,
) -> bool:

    # Check asset_is_available
    asset_states = get_items_for_period(
        items=states,
        asset=asset,
        start=boa.start,
        end=boa.end,
    )
    if not asset_states:
        respects_availability = False
    else:
        respects_availability = all(a.available for a in asset_states)

    if not respects_availability:
        log.warning(f"Asset {asset} could not be used as candidate because not available.")
        return False

    # Check min_zero_time
    if prior_instruction is None:
        respects_min_zero_time = True
    elif current_instruction is not None:
        respects_min_zero_time = True
    else:
        respects_min_zero_time = prior_instruction.end - boa.start > timedelta(minutes=asset.min_zero_time)

    if not respects_min_zero_time:
        log.warning(f"Asset {asset} could not be used as candidate because does not respect min zero time.")
        return False

    # Check min_non_zero_time
    min_non_zero_time = timedelta(minutes=asset.min_non_zero_time)
    if current_instruction is None:
        respects_min_non_zero_time = (boa.end - boa.start) > min_non_zero_time
    else:
        respects_min_non_zero_time = (boa.end - current_instruction.start) > min_non_zero_time

    if not respects_min_non_zero_time:
        log.warning(f"Asset {asset} could not be used as candidate because does not respect min non-zero time.")
        return False

    # If everything passes and the function has got to this stage, then return True.
    return True
