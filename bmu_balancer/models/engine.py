from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from pulp import LpVariable

from bmu_balancer.models.inputs import Asset, BOA
from bmu_balancer.models.outputs import Instruction
from bmu_balancer.operations.utils import SEC_IN_HOUR


@dataclass(frozen=True)
class Candidate:
    asset: Asset
    boa: BOA
    mw: int
    adjusted_start: Optional[datetime] = None
    adjusted_end: Optional[datetime] = None

    @property
    def start(self) -> datetime:
        return self.adjusted_start or self.boa.start

    @property
    def end(self) -> datetime:
        return self.adjusted_end or self.boa.end

    @property
    def hours(self) -> float:
        return (self.end - self.start).seconds / SEC_IN_HOUR

    @property
    def is_import(self) -> bool:
        return self.boa.is_import


@dataclass(frozen=True)
class Variables:
    candidates: Dict[Candidate, LpVariable]

    @property
    def count(self) -> int:
        return len(self.candidates)


@dataclass(frozen=True)
class Solution:
    status: str
    objective: Optional[int] = None
    instructions: Optional[List[Instruction]] = ()
