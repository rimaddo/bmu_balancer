import logging
from datetime import datetime
from typing import Optional, Union

from bmu_balancer.models import Asset, Instruction, Rate
from bmu_balancer.models.engine import Candidate
from bmu_balancer.operations.key_store import KeyStore

log = logging.getLogger(__name__)


def get_prior_instruction(
        asset: Asset,
        time: datetime,
        instructions: KeyStore[Instruction],
) -> Optional[Instruction]:
    """Given a set of instructions, an asset and a time,
    return the instruction for the asset prior to time
    if it exists."""

    asset_instructions = instructions.get(asset=asset)
    asset_instructions.sort(key=lambda x: x.end, reverse=True)

    for asset_instruction in asset_instructions:
        if asset_instruction.end < time:
            return asset_instruction


def get_instruction_cost(
        instruction: Union[Candidate, Instruction],
) -> float:
    """Calculate the cost of delivering the power in an instruction.

    Note: currently this assumes a single ramp rate, but could be easily
    extended to include however many.
    """
    return (
        # Cost of main delivery
        instruction.asset.running_cost_per_mw_hr * instruction.hours
        # cost to deliver ramp up + down
        + get_ramp_cost(instruction=instruction)
    )


def get_ramp_cost(instruction: Union[Candidate, Instruction]) -> float:
    """This is just a vary hacky first step to get something running way to do this,
    will calculate exactly in the future and with multiple rates."""

    if len(instruction.asset.rates) != 1:
        raise RuntimeError(f"{instruction.asset} has {len(instruction.asset.rates)} but only logic for one has been implemented!!")
    rate = instruction.asset.rates[0]

    if rate is None:
        raise RuntimeError(f"Missing rate for asset {instruction.asset}")

    ramp_up_rate = (
        getattr(rate, 'ramp_up_import')
        if instruction.is_import
        else getattr(rate, 'ramp_up_export')
    )
    ramp_up_cost = instruction.mw / ramp_up_rate * 0.5

    ramp_down_rate = (
        getattr(rate, 'ramp_down_import')
        if instruction.is_import
        else getattr(rate, 'ramp_down_export')
    )
    ramp_down_cost = instruction.mw / ramp_down_rate * 0.5

    return ramp_up_cost + ramp_down_cost
