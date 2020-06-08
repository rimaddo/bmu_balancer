from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Dict, Generic, List, Protocol, Tuple, Type, TypeVar, Union

T = TypeVar('T')


@dataclass(frozen=True)
class KeyStore(Generic[T]):
    keys: Union[Tuple[str], List[str]]
    objects: List[T]
    dict: bool = False

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
                        self._equal(obj=obj, attr=attr, val=val)
                        for attr, val in kwargs.items()
                ):
                    self.cache[key].append(obj)

        return self.cache.get(key, [])

    def _equal(self, obj: Union[object, Dict], attr: str, val: Any) -> bool:
        if self.dict:
            return obj.get(attr)
        return getattr(obj, attr) == val

    def __getitem__(self, key: int) -> T:
        return self.objects[key]


class Dataclass(Protocol):
    """Type hint used to identify if something is a dataclass"""
    __dataclass_fields__: Dict


@lru_cache
def get_keys(obj: Type[T]) -> Tuple[str]:
    """Default function to get keys off a dataclass for KeyStore input."""
    return tuple(obj.__annotations__.keys())