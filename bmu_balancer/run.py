from typing import Optional

from bmu_balancer.balance_a_bmu import balance_a_bmu
from bmu_balancer.io.io import dump_solution, load_input_data
from bmu_balancer.models import (BOA, InputData, Instruction, State)
from bmu_balancer.models.engine import Solution
from bmu_balancer.operations.key_store import (
    KeyStore,
    get_keys,
)

SOLVE_INCREMENT = 20


def run(
        input_filepath: str,
        output_filepath: Optional[str] = None,
        visualise: bool = True
) -> None:
    # Load
    data = load_input_data(filepath=input_filepath)

    # Solve
    solution = run_engine(data=data, boa=data.boa, visualise=visualise)

    # Post-solve
    if output_filepath is not None:
        dump_solution(filepath=output_filepath, solution=solution)


def run_all_levels(
        input_filepath: str,
        output_folder: Optional[str] = None,
        visualise: bool = True
) -> None:
    # Load
    data = load_input_data(filepath=input_filepath)

    # Solve
    max_mw = int(data.boa.mw)
    ub = (
        max_mw
        if max_mw % SOLVE_INCREMENT == 0
        else max_mw + SOLVE_INCREMENT
    )
    for n, mw in enumerate(range(0, ub, SOLVE_INCREMENT)):
        boa = BOA(
            id=n,
            start=data.boa.start,
            end=data.boa.end,
            mw=min(mw, max_mw),
            price_mw_hr=data.boa.price_mw_hr,
            bmu=data.boa.bmu,
            rates=data.boa.rates,
        )
        solution = run_engine(data=data, boa=boa, visualise=visualise)

        # Post-solve
        if output_folder is not None:
            output_filepath = f"{output_folder}/{mw}-BOA.json"
            dump_solution(filepath=output_filepath, solution=solution)


def run_engine(data: InputData, boa: BOA, visualise: bool) -> Solution:

    states = KeyStore(keys=get_keys(State), objects=data.states)
    instructions = KeyStore(keys=get_keys(Instruction), objects=data.instructions)

    return balance_a_bmu(
        boa=boa,
        parameters=data.parameters,
        states=states,
        instructions=instructions,
        visualise=visualise,
    )
