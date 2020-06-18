from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')


@dataclass(frozen=True)
class KeyStore(Generic[T]):
    keys: List[str]
    objects: List[T]

    cache = defaultdict(list)

    def get(self, **kwargs) -> List[T]:
        return self._get_values(**kwargs)

    def get_one_or_none(self, **kwargs) -> T:
        values = self._get_values(**kwargs)
        if len(values) == 0:
            return None
        elif len(values) > 1:
            raise RuntimeError
        return values[0]

    def _get_values(self, **kwargs) -> List[T]:
        attr_dict = {k: None for k in self.keys}
        attr_dict.update(**kwargs)
        key = tuple(attr_dict.values())

        if key not in self.cache:
            for obj in self.objects:
                if all(
                    getattr(obj, attr) == val
                    for attr, val in kwargs.items()
                ):
                    self.cache[key].append(obj)

        return self.cache.get(key, [])

    def __getitem__(self, key: int) -> T:
        return self.objects[key]


def get_item_at_time(
        items: KeyStore,
        time: datetime,
        nullable: bool = False,
        **kwargs
) -> Optional:
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
    return [
        item
        for item in items.get(**kwargs)
        if item.start >= start and item.end <= end
    ]
