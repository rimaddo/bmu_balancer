import logging
from datetime import datetime
from typing import List, Optional

from bmu_balancer.models import Asset, BOA

log = logging.getLogger(__name__)

SECS_IN_HR = 60.0 * 60.0
MW_INCREMENT = 10


def get_mw_options(
        asset: Asset,
        boa: BOA,
        increment: int = MW_INCREMENT,
        adjusted_start: datetime = None,
        adjusted_end: datetime = None,
) -> List[int]:

    # Single export / import case
    # In these cases the asset can only be on or off
    # therefore the choice is to keep the asset off
    # i.e. assign zero import / export or to give it
    # it'se set power level.
    if asset.single_import_mw_hr and boa.is_import:
        return [0, -asset.single_import_mw_hr]

    elif asset.single_export_mw_hr and not boa.is_import:
        return [0, asset.single_export_mw_hr]

    mw_bound = get_mw_bound(
        asset=asset,
        boa=boa,
        adjusted_start=adjusted_start,
        adjusted_end=adjusted_end,
    )
    if mw_bound is None:
        mw_bound = boa.mw

    min_bound = mw_bound if mw_bound < 0 else 0
    max_bound = mw_bound if mw_bound > 0 else 0

    options = list(range(min_bound, max_bound + increment, increment))

    log.info(f"Got {len(options)} mw options.")
    return options


def get_mw_bound(
        asset: Asset,
        boa: BOA,
        adjusted_start: Optional[datetime] = None,
        adjusted_end: Optional[datetime] = None,
) -> Optional[int]:

    # Based off capacity
    # For now don't worry about available capacity vs total possible
    start = adjusted_start or boa.start
    end = adjusted_end or boa.end
    delivery_duration_hrs = (end - start).total_seconds() / SECS_IN_HR
    delivery_volume = delivery_duration_hrs * boa.mw
    if abs(delivery_volume) > asset.capacity:
        multiplier = -1 if boa.is_import else 1
        adjusted_volume = int(asset.capacity / delivery_duration_hrs * multiplier)

        log.info(f"Adjusting volume to {adjusted_volume} due to exceeding capacity of {asset.capacity}.")
        return adjusted_volume

    # Based off mw_hr rate
    if boa.is_import:
        return None if boa.mw > -asset.max_import_mw_hr else -asset.max_import_mw_hr
    else:
        return None if boa.mw < asset.max_export_mw_hr else asset.max_export_mw_hr
