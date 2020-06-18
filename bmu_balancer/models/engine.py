from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List

from pulp import LpVariable

from bmu_balancer.models.inputs import Asset, Offer, BOA
from bmu_balancer.models.outputs import Instruction

SEC_IN_HOUR = 3600


@dataclass(frozen=True)
class InstructionCandidate:
    asset: Asset
    boa: BOA
    adjusted_start: Optional[datetime] = None
    adjusted_end: Optional[datetime] = None
    min_mw: Optional[float] = None
    max_mw: Optional[float] = None

    @property
    def start(self) -> datetime:
        return self.adjusted_start or self.boa.start

    @property
    def end(self) -> datetime:
        return self.adjusted_end or self.boa.end

    @property
    def hours(self) -> float:
        return (self.end - self.start).seconds / SEC_IN_HOUR


@dataclass(frozen=True)
class Variables:
    instruction_candidates: Dict[InstructionCandidate, LpVariable]

    @property
    def count(self) -> int:
        return len(self.instruction_candidates)


@dataclass(frozen=True)
class Solution:
    status: str
    objective: Optional[int] = None
    instructions: Optional[List[Instruction]] = None
