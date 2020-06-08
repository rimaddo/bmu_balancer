from datetime import datetime
from typing import List, Optional

from bmu_balancer.operations.key_store import KeyStore

SEC_IN_MIN = 60.0


def get_item_at_time(
        items: KeyStore,
        time: datetime,
        nullable: bool = False,
        **kwargs
) -> Optional:
    """Given a keystore of items and a time,
    return the item at that time if it exists,
    otherwise return none."""
    items_at_time = [
        item
        for item in items.get(**kwargs)
        if item.start <= time <= item.end
    ]

    if len(items_at_time) == 0 and nullable:
        return None

    elif len(items_at_time) != 1:
        raise RuntimeError(
            f"Only expected one item for {kwargs} at {time} got {items_at_time}"
        )

    return items_at_time[0]


def get_items_for_period(
        items: KeyStore,
        start: datetime,
        end: datetime,
        **kwargs
) -> List:
    """Given a keystore of items and a period return
    a list of the items that overlap the period."""
    return [
        item
        for item in items.get(**kwargs)
        if date_range_overlap(
            start_1=start, end_1=end,
            start_2=item.start, end_2=item.end,
        ) > 0
    ]


def date_range_overlap(start_1, end_1, start_2, end_2) -> int:
    latest_start = max(start_1, start_2)
    earliest_end = min(end_1, end_2)
    delta = (earliest_end - latest_start).days + 1
    overlap = max(0, delta)
    return overlap


def timedelta_mins(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / SEC_IN_MIN
