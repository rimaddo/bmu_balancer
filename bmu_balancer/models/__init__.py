from dataclasses import dataclass
from typing import List

from bmu_balancer.models.inputs import Offer, BOA, BMU, AssetState, Rate, Asset
from bmu_balancer.models.outputs import Instruction


@dataclass(frozen=True)
class Data:
    assets: List[Asset]
    rates: List[Rate]
    states: List[AssetState]
    bmus: List[BMU]
    offers: List[Offer]
    instructions: List[Instruction]
    boa: BOA  # A solve is run for a single BOA initially
