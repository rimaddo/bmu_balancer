from bmu_balancer.balance_a_bmu import balance_a_bmu
from tests import SIMPLE_INPUT_FILEPATH


def test_balance_a_bmu() -> None:
    """THe God test to test all things.

    Check that the solver finds an optimal solution for
    this simple problem where the asset is turned on
    not left off with mw of zero.
    """

    solution = balance_a_bmu(input_filepath=SIMPLE_INPUT_FILEPATH)

    assert solution.status == "Optimal"
    assert len(solution.instructions) == 1
    assert solution.instructions[0].mw == 1
