from dataclasses import dataclass
from typing import List

from bmu_balancer.models.inputs import Asset, BMU, BOA, Parameters, Rate, State
from bmu_balancer.models.outputs import Instruction


@dataclass(frozen=True)
class InputData:
    parameters: Parameters
    assets: List[Asset]
    states: List[State]
    bmus: List[BMU]
    instructions: List[Instruction]
    boa: BOA  # A solve is run for a single BOA initially

    def __repr__(self) -> str:
        return "InputData"
