from typing import Optional

from bmu_balancer.engine.main import run_engine
from bmu_balancer.io.io import dump_solution, load_input_data
from bmu_balancer.models import AssetState, Instruction, Rate
from bmu_balancer.models.engine import Solution
from bmu_balancer.operations.pre_solve.generate_instruction_candidates import generate_instruction_candidates
from bmu_balancer.operations.key_store import KeyStore, get_keys


def balance_a_bmu(input_filepath: str, output_filepath: Optional[str] = None) -> Solution:

    data = load_input_data(filepath=input_filepath)

    # Pre-solve
    instruction_candidates = generate_instruction_candidates(
        boa=data.boa,
        states=KeyStore(keys=get_keys(AssetState), objects=data.states),
        instructions=KeyStore(keys=get_keys(Instruction), objects=data.instructions),
    )

    # Engine
    solution = run_engine(
        boa=data.boa,
        rates=KeyStore(keys=get_keys(Rate), objects=data.rates),
        instruction_candidates=instruction_candidates,
    )

    # Post-solve
    if output_filepath is not None:
        dump_solution(filepath=output_filepath, solution=solution)

    return solution
