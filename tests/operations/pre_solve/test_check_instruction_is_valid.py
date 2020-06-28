from datetime import datetime
from typing import Any, Dict

import pytest

from bmu_balancer.models import State
from bmu_balancer.operations.key_store import KeyStore, get_keys
from bmu_balancer.operations.pre_solve.check_instruction_is_valid import asset_can_be_assigned_to_boa
from tests.factories import AssetFactory, BOAFactory, InstructionFactory, StateFactory


@pytest.fixture
def asset_can_be_assigned_to_boa_fixtures(
        asset: AssetFactory,
        boa: BOAFactory,
        previous_instruction: InstructionFactory,
        current_instruction: InstructionFactory,
) -> Dict[int, Dict[str, Any]]:

    keys = get_keys(State)

    state_available = StateFactory(
        asset=asset,
        start=datetime(2000, 1, 1),
        end=datetime(2000, 2, 1),
        available=True,
    )

    return {
        # 1: Asset can be assigned, withOUT previous and current
        1: {
                "boa": boa,
                "states": KeyStore(
                    keys=keys,
                    objects=[state_available],
                ),
                "output": True,
        },
        # 2: Asset can be assigned, with previous and current
        2: {
            "boa": boa,
            "states": KeyStore(
                keys=keys,
                objects=[state_available],
            ),
            "current_instruction": current_instruction,
            "prior_instruction": previous_instruction,
            "output": True,
        },
        # 3: Asset does not respect availability
        3: {
            "boa": boa,
            "states": KeyStore(
                keys=keys,
                objects=[
                    state_available,
                    StateFactory(
                        asset=asset,
                        start=datetime(2000, 1, 1),
                        end=datetime(2000, 2, 1),
                        available=False,
                    )
                ]
            ),
            "output": False,
        },
        # 4: Asset does not respect min zero time
        4: {
            "boa": boa,
            "states": KeyStore(
                keys=keys,
                objects=[state_available],
            ),
            "prior_instruction": InstructionFactory(end=datetime(2000, 1, 1, 9)),
            "output": False,
        },
        # 5: Asset does not respect min non-zero time withOUT current instr
        5: {
                "boa": BOAFactory(
                    start=datetime(2000, 1, 1, 0, 0),
                    end=datetime(2000, 1, 1, 0, 1),
                ),
                "states": KeyStore(
                    keys=keys,
                    objects=[state_available],
                ),
                "output": False,
        },
        # 6: Asset does not respect min non-zero time with current instr
        6: {
            "boa": BOAFactory(
                start=datetime(2000, 1, 1, 0, 1),
                end=datetime(2000, 1, 1, 0, 3),
            ),
            "states": KeyStore(
                keys=keys,
                objects=[state_available],
            ),
            "current_instruction": InstructionFactory(
                start=datetime(2000, 1, 1, 0, 0),
                end=datetime(2000, 1, 1, 0, 2),
            ),
            "output": False,
        },
    }


@pytest.mark.parametrize(
    "index",
    [1, 2, 3, 4, 5, 6],
    ids=[
        "1: Asset can be assigned, withOUT previous and current",
        "2: Asset can be assigned, with previous and current",
        "3: Asset does not respect availability",
        "4: Asset does not respect min zero time",
        "5: Asset does not respect min non-zero time",
        "6 Asset does not respect min non-zero time with current instr",
    ]
)
def test_asset_can_be_assigned_to_boa(
        index: int,
        asset_can_be_assigned_to_boa_fixtures: Dict[int, Dict[str, Any]],
        asset: AssetFactory,
) -> None:
    fixtures = asset_can_be_assigned_to_boa_fixtures.get(index)

    output = asset_can_be_assigned_to_boa(
        asset=asset,
        boa=fixtures["boa"],
        states=fixtures["states"],
        current_instruction=fixtures.get("current_instruction"),
        prior_instruction=fixtures.get("prior_instruction"),
    )

    assert fixtures["output"] == output
