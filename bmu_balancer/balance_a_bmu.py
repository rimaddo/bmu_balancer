from bmu_balancer.engine.main import run_engine
from bmu_balancer.models import InputData, Instruction, Rate, State
from bmu_balancer.models.engine import Candidate, Solution
from bmu_balancer.operations.key_store import KeyStore, get_keys
from bmu_balancer.operations.post_solve.plot import plot
from bmu_balancer.operations.pre_solve.generate_instruction_candidates import generate_instruction_candidates


def balance_a_bmu(
        data: InputData,
        visualise: bool = False,
) -> Solution:

    # Pre-solve
    rates = KeyStore(keys=get_keys(Rate), objects=data.rates)
    states = KeyStore(keys=get_keys(State), objects=data.states)
    instructions = KeyStore(keys=get_keys(Instruction), objects=data.instructions)
    candidates = generate_instruction_candidates(
        boa=data.boa,
        states=states,
        instructions=instructions,
        execution_time=data.parameters.execution_time,
    )

    # Engine
    solution = run_engine(
        boa=data.boa,
        rates=rates,
        candidates=candidates,
    )

    if visualise:
        candidates = KeyStore(keys=get_keys(Candidate), objects=candidates)
        sol_instructions = KeyStore(keys=get_keys(Instruction), objects=solution.instructions)
        plot(
            boa=data.boa,
            rates=rates,
            candidates=candidates,
            instructions=sol_instructions,
        )

    return solution
