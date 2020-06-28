from datetime import datetime, timedelta

from bmu_balancer.models import Instruction, State
from bmu_balancer.operations.key_store import KeyStore, get_keys
from bmu_balancer.operations.pre_solve.generate_instruction_candidates import generate_instruction_candidates
from tests.factories import AssetFactory, BOAFactory, StateFactory


def test_generate_instruction_candidates(asset: AssetFactory, boa: BOAFactory) -> None:
    """Since each sub-function is tested more thoroughly and directly
    this is only tested in a high-level way."""
    states = KeyStore(
        keys=get_keys(State),
        objects={
            StateFactory(
                asset=asset,
                start=boa.start - timedelta(hours=1),
                end=boa.end + timedelta(hours=1),
                available=True,
                charge=200,
            )
        }
    )
    instructions = KeyStore(
        keys=get_keys(Instruction),
        objects=[],
    )

    output = generate_instruction_candidates(
        boa=boa,
        states=states,
        instructions=instructions,
        execution_time=datetime(2000, 1, 1),
    )

    assert len(output) == 21
