from datetime import datetime, timedelta
from typing import Any, Dict

import pytest

from bmu_balancer.operations.pre_solve.get_adjusted_times import NOW, get_adjusted_end, get_adjusted_start
from tests.factories import AssetFactory, BOAFactory, InstructionFactory


@pytest.fixture
def get_adjusted_start_fixtures(
        asset: AssetFactory,
        boa: BOAFactory,
        current_instruction: InstructionFactory,
) -> Dict[int, Dict[str, Any]]:

    future_boa = BOAFactory(
        start=NOW + timedelta(minutes=asset.notice_to_deviate_from_zero + 5),
    )

    return {
        # 1: valid with current instruction
        1: {
            "current_instruction": InstructionFactory(
                end=NOW,
            ),
            "boa": future_boa,
            "output": None,
        },
        # 2: valid without current instruction
        2: {
            "current_instruction": None,
            "boa": future_boa,
            "output": None,
        },
        # 3: invalid, not enough notice to deliver bid
        3: {
            "current_instruction": InstructionFactory(
                end=NOW + timedelta(minutes=asset.notice_to_deliver_bid - 5),
            ),
            "boa": boa,
            "output": NOW + timedelta(minutes=asset.notice_to_deliver_bid),
        },
        # 4: invalid, not enough time to deviate from zero
        4: {
            "current_instruction": None,
            "boa": BOAFactory(
                start=NOW + timedelta(minutes=asset.notice_to_deviate_from_zero - 5),
            ),
            "output": NOW + timedelta(minutes=asset.notice_to_deliver_bid),
        }
    }


@pytest.mark.parametrize(
    "index",
    [1, 2, 3, 4],
    ids=[
        "1: valid with current instruction",
        "2: valid without current instruction",
        "3: invalid, not enough notice to deliver bid",
        "4: invalid, not enough time to deviate from zero",
    ]
)
def test_get_adjusted_start(index: int, get_adjusted_start_fixtures: Dict, asset: AssetFactory) -> None:

    fixtures = get_adjusted_start_fixtures.get(index, {})

    output = get_adjusted_start(
        asset=asset,
        boa=fixtures.get("boa"),
        current_instruction=fixtures.get("current_instruction"),
    )

    assert output == fixtures.get("output")


@pytest.fixture
def get_adjusted_end_fixtures(asset: AssetFactory, boa: BOAFactory) -> Dict[int, Dict[str, Any]]:

    short_instruction = InstructionFactory(
        start=datetime(2000, 1, 1, 1, 0),
        end=datetime(2000, 1, 1, 1, 10),
    )
    short_boa = BOAFactory(
        start=datetime(2000, 1, 1, 1, 10),
        end=datetime(2000, 1, 1, 1, 20),
    )

    return {
        # 1: valid without current instruction
        1: {
            "boa": boa,
            "current_instruction": None,
            "adjusted_start": None,
            "output": None,
        },
        # 2: valid with current instruction
        2: {
            "boa": short_boa,
            "current_instruction": short_instruction,
            "adjusted_start": None,
            "output": None,
        },
        # 3: no current instruction, boa is longer than max runtime, has no adjusted start
        3: {
            "boa": BOAFactory(
                start=datetime(2000, 1, 1, 1, 00),
                end=datetime(2000, 1, 1, 1, 40),
            ),
            "current_instruction": None,
            "adjusted_start": None,
            "output": datetime(2000, 1, 1, 1, 30),
        },
        # 4: no current instruction, boa is longer than max runtime, has adjusted start
        4: {
            "boa": BOAFactory(
                start=datetime(2000, 1, 1, 1, 00),
                end=datetime(2000, 1, 1, 1, 40),
            ),
            "current_instruction": None,
            "adjusted_start": datetime(2000, 1, 1, 1, 5),
            "output": datetime(2000, 1, 1, 1, 35),
        },
        # 5: current instruction with boa is longer than max runtime
        5: {
            "boa": BOAFactory(
                start=datetime(2000, 1, 1, 1, 20),
                end=datetime(2000, 1, 1, 1, 40),
            ),
            "current_instruction": InstructionFactory(
                start=datetime(2000, 1, 1, 1, 0),
                end=datetime(2000, 1, 1, 1, 20),
            ),
            "adjusted_start": None,
            "output": datetime(2000, 1, 1, 1, 30),
        },
        # 6: current instruction with boa is longer than max runtime, with adjusted start
        6: {
            "boa": BOAFactory(
                start=datetime(2000, 1, 1, 1, 20),
                end=datetime(2000, 1, 1, 1, 40),
            ),
            "current_instruction": InstructionFactory(
                start=datetime(2000, 1, 1, 1, 0),
                end=datetime(2000, 1, 1, 1, 20),
            ),
            "adjusted_start": datetime(2000, 1, 1, 1, 5),
            "output": datetime(2000, 1, 1, 1, 35),
        },
    }


@pytest.mark.parametrize(
    "index",
    [1, 2, 3, 4, 5, 6],
    ids=[
        "1: valid without current instruction",
        "2: valid with current instruction",
        "3: no current instruction, boa is longer than max runtime, has no adjusted start",
        "4: no current instruction, boa is longer than max runtime, has adjusted start",
        "5: current instruction with boa is longer than max runtime",
        "6: current instruction with boa is longer than max runtime, with adjusted start",
    ]
)
def test_get_adjusted_end(
        index: int,
        get_adjusted_end_fixtures: Dict[int, Dict[str, Any]],
        asset: AssetFactory,
) -> None:

    fixtures = get_adjusted_end_fixtures.get(index, {})

    output = get_adjusted_end(
        asset=asset,
        boa=fixtures.get("boa"),
        current_instruction=fixtures.get("current_instruction"),
        adjusted_start=fixtures.get("adjusted_start"),
    )

    assert fixtures.get("output") == output
