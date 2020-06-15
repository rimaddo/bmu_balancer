from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bmu_balancer.models.inputs import Asset, BOA
from bmu_balancer.operations.utils import SEC_IN_HOUR


@dataclass(frozen=True)
class Instruction:
    asset: Asset
    mw: int
    start: datetime
    end: datetime
    id: Optional[int] = None
    boa: Optional[BOA] = None

    def __repr__(self) -> str:
        return f"Instruction({self.asset}: {self.start} till {self.end} at {self.mw})"

    @property
    def hours(self) -> float:
        return (self.end - self.start).seconds / SEC_IN_HOUR