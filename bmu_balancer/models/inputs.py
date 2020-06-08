from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
class Rate:
    id: int
    asset: Asset
    ramp_up_import: float
    ramp_up_export: float
    ramp_down_import: float
    ramp_down_export: float
    min_mw: int
    max_mw: Optional[int]


@dataclass(frozen=True)
class AssetState:
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
    assets: List[Asset]

    def __repr__(self) -> str:
        return f"BMU({self.name or self.id})"


@dataclass(frozen=True)
class Offer:
    id: int
    bmu: BMU
    start: Optional[datetime]
    end: Optional[datetime]
    price_mw_hr: float


@dataclass(frozen=True)
class BOA:
    id: int
    start: datetime
    end: datetime
    mw: int
    offer: Offer

    @property
    def price_mw_hr(self) -> float:
        return self.offer.price_mw_hr

    @property
    def assets(self) -> List[Asset]:
        return self.offer.bmu.assets

    @property
    def is_import(self) -> bool:
        return self.mw < 0
