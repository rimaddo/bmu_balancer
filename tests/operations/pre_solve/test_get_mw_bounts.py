from datetime import datetime
from typing import List

import pytest

from bmu_balancer.operations.pre_solve.get_mw_bounds import get_mw_bound, get_mw_options
from tests.factories import AssetFactory, BOAFactory

START = datetime(2000, 1, 1, 1)
END = datetime(2000, 1, 1, 2)


@pytest.mark.parametrize(
    "boa, expected_output",
    [
        # 1. Import, boa is less than max_import_mw_hr
        (BOAFactory(mw=-1, start=START, end=END), None),
        # 2. Import, boa is more than max_import_mw_hr
        (BOAFactory(mw=-101, start=START, end=END), -100),
        # 3. Export, boa is less than max_export_mw_hr
        (BOAFactory(mw=1, start=START, end=END), None),
        # 4. Export, boa is more than max_export_mw_hr
        (BOAFactory(mw=101, start=START, end=END), 100),
        # 5. Import boa exceeds capacity
        (BOAFactory(mw=400, start=START, end=END), 200),
        # 6. Export boa exceeds capacity
        (BOAFactory(mw=-400, start=START, end=END), -200),
    ],
)
def test_get_mw_bound(boa: BOAFactory, expected_output: int, asset: AssetFactory) -> None:
    output = get_mw_bound(
        boa=boa,
        asset=asset,
    )
    assert output == expected_output


@pytest.mark.parametrize(
    "boa, expected_output",
    [
        # 1. Import, amount is less than capacity
        (BOAFactory(mw=-50, start=START, end=END), [-50, 0]),
        # 2. Import, amount is more than capacity
        (BOAFactory(mw=-400, start=START, end=END), [-200, -150, -100, -50, 0]),
        # 3. Export, amount is less than capacity
        (BOAFactory(mw=50, start=START, end=END), [0, 50]),
        # 4. Export, amount is more than capacity
        (BOAFactory(mw=400, start=START, end=END), [0, 50, 100, 150, 200]),

    ],
)
def test_get_mw_options(boa: BOAFactory, expected_output: List[int], asset: AssetFactory) -> None:
    output = get_mw_options(
        asset=asset,
        boa=boa,
        increment=50,
    )
    # assert output == expected_output
    assert output == expected_output
