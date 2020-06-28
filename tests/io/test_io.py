
from bmu_balancer.io.io import load_input_data
from bmu_balancer.models import BOA, InputData
from tests import SIMPLE_INPUT_FILEPATH


def test_load_input_data():
    data = load_input_data(filepath=SIMPLE_INPUT_FILEPATH)
    assert type(data) == InputData
    assert len(data.assets) == 2
    assert len(data.rates) == 2
    assert len(data.states) == 2
    assert len(data.bmus) == 1
    assert len(data.instructions) == 1
    assert type(data.boa) == BOA
