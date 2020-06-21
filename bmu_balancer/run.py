from typing import Optional

from bmu_balancer.balance_a_bmu import balance_a_bmu
from bmu_balancer.io.io import dump_solution, load_input_data


def run(
        input_filepath: str,
        output_filepath: Optional[str] = None,
        visualise: bool = True
) -> None:
    # Load
    data = load_input_data(filepath=input_filepath)

    solution = balance_a_bmu(
        data=data,
        visualise=visualise,
    )

    # Post-solve
    if output_filepath is not None:
        dump_solution(filepath=output_filepath, solution=solution)
