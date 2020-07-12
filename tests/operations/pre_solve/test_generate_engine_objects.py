from datetime import datetime, timedelta

import pytest

from bmu_balancer.models import Instruction, State
from bmu_balancer.operations.key_store import KeyStore, get_keys
from bmu_balancer.operations.pre_solve.generate_engine_objects import (
    generate_assignment_candidates,
    generate_instruction_candidates,
)
from tests.factories import AssetFactory, BOAFactory, StateFactory


@pytest.fixture
def states(asset: AssetFactory, boa: BOAFactory) -> KeyStore[StateFactory]:
    return KeyStore(
        keys=get_keys(State),
        objects={
            StateFactory(
                asset=asset,
                start=boa.start - timedelta(hours=1),
                end=boa.end + timedelta(hours=1),
                available=True,
                charge=0,
            )
        }
    )


@pytest.fixture
def instructions() -> KeyStore[Instruction]:
    return KeyStore(
        keys=get_keys(Instruction),
        objects=[],
    )


def test_generate_assignment_candidates(
        boa: BOAFactory,
        states: KeyStore[StateFactory],
        instructions: KeyStore[Instruction],
) -> None:

    output = generate_assignment_candidates(
        boa=boa,
        states=states,
        instructions=instructions,
        execution_time=datetime(2000, 1, 1),
    )

    assert len(list(output)) == 1


def test_generate_instruction_candidates(
        boa: BOAFactory,
        states: KeyStore[StateFactory],
        instructions: KeyStore[Instruction],
) -> None:
    """Since each sub-function is tested more thoroughly and directly
    this is only tested in a high-level way."""

    output = generate_instruction_candidates(
        boa=boa,
        states=states,
        instructions=instructions,
        execution_time=datetime(2000, 1, 1),
    )

    # assert len(output) == 21
    for asset in boa.assets:
        assert len(output[asset]) == 11
