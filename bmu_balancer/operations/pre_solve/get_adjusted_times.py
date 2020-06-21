import logging
from datetime import datetime, timedelta
from typing import Optional

from bmu_balancer.models import Asset, BOA, Instruction

log = logging.getLogger(__name__)

NOW = datetime.utcnow()


def get_adjusted_start(
        asset: Asset,
        boa: BOA,
        current_instruction: Optional[Instruction],
        execution_time: datetime = NOW,
) -> Optional[datetime]:
    """Check that the asset respects starting criteria.

    This provides an adjusted start time, which is None if the boa start is acceptable
    or is as early as is feasible given the constraints if not.
    An adjusted later start time can then be penalised for later in the objective.
    """

    # If the asset is on, only need to worry about bid
    earliest_deliver_bid = execution_time + timedelta(minutes=asset.notice_to_deliver_bid)
    # If the asset has an instruction and thus is already on,
    # and the earliest it can deliver is after the boa start,
    # then return the earliest time as the adjusted start.
    if current_instruction is not None and boa.start < earliest_deliver_bid:
        log.warning(
            f"earliest_deliver_bid: Start time of {asset} adjusted"
            f"from {boa.start} to {earliest_deliver_bid}"
        )
        return earliest_deliver_bid

    # If the asset is not on, need to make sure it has enough time to switch on.
    # Given a start time before the non-zero notice period or the bid delivery
    # then return the larger of the two.
    earliest_non_zero = execution_time + timedelta(minutes=asset.notice_to_deviate_from_zero)
    if boa.start < earliest_non_zero or boa.start < earliest_deliver_bid:
        notice_to_deviate_from_zero = max(earliest_deliver_bid, earliest_non_zero)
        log.warning(
            f"{asset} cannot switch on at start because of insufficient notice, "
            f"start adjusted to {notice_to_deviate_from_zero}"
        )
        return notice_to_deviate_from_zero

    # If all the prior passes, then the boa start is acceptable, return no adjustment.
    return None


def get_adjusted_end(
        asset: Asset,
        boa: BOA,
        current_instruction: Optional[Instruction],
        adjusted_start: Optional[datetime],
) -> Optional[datetime]:

    max_delivery = timedelta(minutes=asset.max_delivery_period)
    boa_duration = boa.end - boa.start

    # Cases where there is no existing instruction
    if current_instruction is None and boa_duration <= max_delivery:
        # Given a runtime less than the max, there is no need to adjust the end.
        return None

    elif current_instruction is None and boa_duration > max_delivery:
        # If the runtime is greater however, turn on for as long as possible.
        start = adjusted_start or boa.start
        end = start + max_delivery
        log.warning(f"{asset} max runtime {max_delivery} exceeded, reducing delivery end to {end}.")
        return end

    # Cases where there is an existing instruction
    inst_and_boa_duration = boa.end - current_instruction.start
    if inst_and_boa_duration > max_delivery:
        start = adjusted_start or current_instruction.start
        end = start + max_delivery
        log.warning(
            f"{asset} max runtime {max_delivery} exceeded because of existing instruction, "
            f"reducing delivery end to {end}."
        )
        return end

    return None
