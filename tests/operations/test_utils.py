from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import pytest

from bmu_balancer.operations.key_store import KeyStore
from bmu_balancer.operations.utils import get_item_at_time, get_items_for_period


@dataclass
class Item:
    name: str
    start: datetime
    end: datetime
    type: str


ITEM_ONE = Item(name="Orange", start=datetime(2000, 1, 1), end=datetime(2000, 1, 1, 1), type="Fruit")
ITEM_TWO = Item(name="Apple", start=datetime(2000, 1, 2), end=datetime(2000, 1, 2, 1), type="Fruit")
ITEM_THREE = Item(name="Carrot", start=datetime(2000, 1, 1), end=datetime(2000, 1, 1, 1), type="Vegetable")
ITEM_FOUR = Item(name="Carrot", start=datetime(2000, 1, 3), end=datetime(2000, 1, 3, 1), type="Vegetable")


TEST_KEY_STORE = KeyStore(
    keys=["name", "time", "type"],
    objects=[
        ITEM_ONE,
        ITEM_TWO,
        ITEM_THREE,
        ITEM_FOUR,
    ],
)


@pytest.mark.parametrize(
    "items, time, nullable, kwargs, expected_output",
    [
        # No items at time, nullable
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 10),
            True,
            {},
            None,
        ),
        # One item at time
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 2),
            True,
            {},
            ITEM_TWO,
        ),
        # One item at time with kwargs,
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 1),
            True,
            {"type": "Vegetable"},
            ITEM_THREE,
        ),
    ]
)
def test_get_item_at_time(
        items: KeyStore,
        time: datetime,
        nullable: bool,
        kwargs: Dict[str, Any],
        expected_output: object,
) -> None:

    output = get_item_at_time(
        items=items,
        time=time,
        nullable=nullable,
        **kwargs
    )
    assert output == expected_output


@pytest.mark.parametrize(
    "items, time, nullable, kwargs, expected_output",
    [
        # No items at time, not nullable
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 10),
            False,
            {},
            Exception,
        ),
        # More than one item at time
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 1),
            True,
            {},
            None
        ),
    ]
)
def test_get_item_at_time__raises_exception(
        items: KeyStore,
        time: datetime,
        nullable: bool,
        kwargs: Dict,
        expected_output: object,
) -> None:

    with pytest.raises(Exception):
        get_item_at_time(
            items=items,
            time=time,
            nullable=nullable,
            **kwargs
        )


@pytest.mark.parametrize(
    "items, start, end, kwargs, expected_output",
    [
        # No items in period
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 10),
            datetime(2000, 1, 11),
            {},
            []
        ),
        # One item in period
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 2),
            datetime(2000, 1, 2, 12),
            {},
            [ITEM_TWO]
        ),
        # One item in period given kwargs
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 1),
            datetime(2000, 1, 2),
            {"type": "Vegetable"},
            [ITEM_THREE]
        ),
        # More than one item in period
        (
            TEST_KEY_STORE,
            datetime(2000, 1, 1),
            datetime(2000, 1, 1, 23),
            {},
            [ITEM_ONE, ITEM_THREE]
        ),
    ]
)
def test_get_items_for_period(
        items: KeyStore[Item],
        start: datetime,
        end: datetime,
        kwargs: Dict[str, Any],
        expected_output: List[Item]
) -> None:
    output = get_items_for_period(
        items=items,
        start=start,
        end=end,
        **kwargs,
    )
    assert output == expected_output
