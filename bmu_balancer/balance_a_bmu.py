from dis import Instruction
from typing import Optional, List

from bmu_balancer.engine.main import run_engine
from bmu_balancer.models import Data, BOA
from bmu_balancer.models.engine import Solution, InstructionCandidate
from bmu_balancer.utils import KeyStore


def balance_a_bmu(input_filepath: str, output_filepath: Optional[str]) -> None:

    data = load_data(filepath=input_filepath)

    # Pre-solve
    instruction_candidates = generate_instruction_candidates(
        boa=data.boa,
        states=KeyStore(keys=['asset'], objects=data.states),
        instructions=KeyStore(keys=['asset'], objects=data.instructions),
    )

    # Engine
    solution = run_engine(
        boa=data.boa,
        rates=KeyStore(keys=['asset'], objects=data.rates),
        instruction_candidates=instruction_candidates,
    )

    # Post-solve
    if output_filepath is not None:
        save_data(filepath=output_filepath, solution=solution)


def load_data(filepath: str) -> Data:
    # Todo
    pass


def generate_instruction_candidates(
        boa: BOA,
        states: KeyStore,
        instructions: KeyStore[Instruction],
) -> List[InstructionCandidate]:
    # Todo
    pass


def save_data(filepath: str, solution: Solution) -> None:
    # Todo
    pass
