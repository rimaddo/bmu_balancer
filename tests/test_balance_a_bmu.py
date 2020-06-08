from bmu_balancer.balance_a_bmu import balance_a_bmu
from tests import SIMPLE_INPUT_FILEPATH


def test_balance_a_bmu() -> None:
    """THe God test to test all things."""

    solution = balance_a_bmu(input_filepath=SIMPLE_INPUT_FILEPATH)
