from dataclasses import dataclass
from datetime import datetime
from typing import Collection, Optional


@dataclass(frozen=True)
class Asset:
    """An asset is any item that has the ability
    to import or export power to the grid."""
    id: int
    slug: Optional[str]
    capacity: float
    # Costs
    running_cost_per_mw_hr: float
    min_required_profit: float = 0
    # Constraints
    max_import_mw_hr: float = 0
    max_export_mw_hr: float = 0
    min_zero_time: float = 0
    min_non_zero_time: float = 0
    notice_to_deviate_from_zero: float = 0
    max_delivery_period: Optional[float] = None

    def __repr__(self) -> str:
        return f"Asset({self.slug or self.id})"


@dataclass(frozen=True)
class Rate:
    asset: Asset
    ramp_up_import: float
    ramp_up_export: float
    ramp_down_import: float
    ramp_down_export: float
    min_mw: int = 0
    max_mw: Optional[int] = None


@dataclass(frozen=True)
class AssetState:
    asset: Asset
    charge: int
    time: datetime


@dataclass(frozen=True)
class BMU:
    """A BM Unit is a collection of assets which respond together
    from national grids perspective to deliver a request."""
    id: int
    assets: Collection[Asset]
    name: Optional[str] = None

    def __repr__(self) -> str:
        return f"BMU({self.name or self.id})"


@dataclass(frozen=True)
class Offer:
    bmu: BMU
    offer_start: datetime
    offer_end: datetime
    price_mw_hr: float
    boa_start: Optional[datetime] = None
    boa_end: Optional[datetime] = None
    boa_value: Optional[int] = None
