from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bmu_balancer.models.inputs import Asset, BOA


@dataclass(frozen=True)
class Instruction:
    asset: Asset
    mw: int
    start: datetime
    end: datetime
    boa: Optional[BOA] = None
