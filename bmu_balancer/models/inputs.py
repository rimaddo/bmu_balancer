from dataclasses import dataclass
from datetime import datetime
from typing import Collection, Optional, Tuple


@dataclass(frozen=True)
class Parameters:
    execution_time: datetime


@dataclass(frozen=True)
class Rate:
    id: int
    ramp_up_import: float
    ramp_up_export: float
    ramp_down_import: float
    ramp_down_export: float
    min_mw: int
    max_mw: Optional[int]


@dataclass(frozen=True)
class Asset:
    """An asset is any item that has the ability
    to import or export power to the grid."""
    id: int
    name: Optional[str]
    capacity: float
    # Costs
    running_cost_per_mw_hr: float
    min_required_profit: float
    # Ramps
    rates: Tuple[Rate]
    # Constraints
    max_import_mw_hr: float
    max_export_mw_hr: float
    single_import_mw_hr: Optional[float]
    single_export_mw_hr: Optional[float]
    min_zero_time: float
    min_non_zero_time: float
    notice_to_deviate_from_zero: float
    notice_to_deliver_bid: float
    max_delivery_period: Optional[float]

    def __repr__(self) -> str:
        return f"Asset({self.name or self.id})"


@dataclass(frozen=True)
class State:
    id: int
    asset: Asset
    start: datetime
    end: datetime
    charge: int
    available: bool


@dataclass(frozen=True)
class BMU:
    """A BM Unit is a collection of assets which respond together
    from national grids perspective to deliver a request."""
    id: int
    name: Optional[str]
    assets: Tuple[Asset]

    def __repr__(self) -> str:
        return f"BMU({self.name or self.id})"


@dataclass(frozen=True)
class BOA:
    id: int
    start: datetime
    end: datetime
    price_mw_hr: float
    mw: int
    bmu: BMU
    rates: Collection[Rate]

    @property
    def assets(self) -> Tuple[Asset]:
        return self.bmu.assets

    @property
    def is_import(self) -> bool:
        return self.mw < 0

    def __repr__(self) -> str:
        return f"BOA(start: {self.start.isoformat()}, end: {self.end.isoformat()}, mw: {self.mw}, price: {self.price_mw_hr})"
