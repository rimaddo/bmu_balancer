from datetime import datetime
from typing import Optional

from bmu_balancer.models import Asset, Instruction
from bmu_balancer.operations.key_store import KeyStore


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
