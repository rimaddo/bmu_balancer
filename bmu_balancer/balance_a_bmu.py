import logging

from bmu_balancer.engine.main import run_engine
from bmu_balancer.models import BOA, Instruction, Parameters, State
from bmu_balancer.models.engine import Solution
from bmu_balancer.operations.key_store import KeyStore, get_keys
from bmu_balancer.operations.post_solve.plot import plot
from bmu_balancer.operations.pre_solve.generate_engine_objects import (
    generate_assignment_candidates,
    generate_instruction_candidates,
)

log = logging.getLogger(__name__)


def balance_a_bmu(
        boa: BOA,
        parameters: Parameters,
        states: KeyStore[State],
        instructions: KeyStore[Instruction],
        visualise: bool,
) -> Solution:

    # Pre-solve
    states = KeyStore(keys=get_keys(State), objects=states)
    instructions = KeyStore(keys=get_keys(Instruction), objects=instructions)
    candidates = generate_instruction_candidates(
        boa=boa,
        states=states,
        instructions=instructions,
        execution_time=parameters.execution_time,
    )
    assignments = generate_assignment_candidates(candidates=candidates)

    # Engine
    solution = run_engine(
        boa=boa,
        assignments=assignments,
    )

    if visualise:
        sol_instructions = KeyStore(keys=get_keys(Instruction), objects=solution.instructions)
        plot(
            boa=boa,
            candidates=candidates,
            instructions=sol_instructions,
        )

    return solution
