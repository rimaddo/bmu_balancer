from datetime import datetime
from typing import Any, Dict

import pytest

from bmu_balancer.models import Asset, Instruction
from bmu_balancer.operations.instruction_helpers import get_prior_instruction
from bmu_balancer.operations.key_store import KeyStore, get_keys
from tests.factories import InstructionFactory


@pytest.fixture
def get_prior_instruction_fixtures(asset: Asset) -> Dict:
    """Fixtures associated with the test_get_prior_instruction tests."""

    past_2 = InstructionFactory(asset=asset, end=datetime(1999, 12, 31, 0))
    past_1 = InstructionFactory(asset=asset, end=datetime(1999, 12, 31, 12))
    future_1 = InstructionFactory(asset=asset, end=datetime(2000, 1, 1, 12))
    future_2 = InstructionFactory(asset=asset, end=datetime(2000, 1, 2))
    other_1 = InstructionFactory()
    other_2 = InstructionFactory()

    return {
        # 1: Single asset, instruction before time exists
        1: {
            "asset": asset,
            "time": datetime(2000, 1, 1, 0, 0),
            "instructions": KeyStore(
                keys=get_keys(Instruction),
                objects=[past_2, past_1, future_1, future_2, other_1, other_2],
            ),
            "output": past_1
        },
        # 2: Single asset, instruction before time does not exist
        2: {
            "asset": asset,
            "time": datetime(2000, 1, 1, 0, 0),
            "instructions": KeyStore(
                keys=get_keys(Instruction),
                objects=[future_1, future_2, other_1, other_2],
            ),
            "output": None
        },
        # 3: Different asset only
        3: {
            "asset": asset,
            "time": datetime(2000, 1, 1, 0, 0),
            "instructions": KeyStore(
                keys=get_keys(Instruction),
                objects=[other_1, other_2],
            ),
            "output": None
        },
    }


@pytest.mark.parametrize(
    "index",
    [1, 2, 3],
    ids=[
        "1: Single asset, instruction before time exists",
        "2: Single asset, instruction before time does not exist",
        "3: Different asset only",
    ],
)
def test_get_prior_instruction(
        index: int,
        get_prior_instruction_fixtures: Dict[int, Dict[str, Any]],
) -> None:

    fixtures = get_prior_instruction_fixtures[index]

    output = get_prior_instruction(
        asset=fixtures['asset'],
        time=fixtures['time'],
        instructions=fixtures['instructions'],
    )

    assert output == fixtures['output']
