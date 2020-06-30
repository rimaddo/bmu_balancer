from datetime import datetime
from typing import Dict, Tuple

import pytest

from bmu_balancer.engine.main import run_engine
from bmu_balancer.models import Asset
from bmu_balancer.models.engine import Candidate
from tests.factories import AssetFactory, BOAFactory, RateFactory

RATE = RateFactory(
    ramp_up_import=1,
    ramp_up_export=1,
    ramp_down_import=1,
    ramp_down_export=1,
)

UNDER_MIN_REQUIRED_PROFIT = [
    # Check that don't choose to turn on an asset if the
    # profit is less than the required profit to activate.
    # In this case;
    #      price_mw_hr * hours >= min_required_profit
    #        10             * 3     >= 10
    #  fails.
    AssetFactory(
        name="one",
        min_required_profit=100,
        rates=tuple([RATE]),
    )
]

OVER_MIN_REQUIRED_PROFIT = [
    # Check that an asset will turn on if the profit is higher
    # than the threshold.
    # In this case;
    #      price_mw_hr * hours >= min_required_profit
    #      10              *  3     >= 1
    #  passes.
    AssetFactory(
        name="one",
        min_required_profit=10,
        rates=tuple([RATE]),
    )
]


MINIMISE_COST_PER_MW = [
    # Check that when given two assets it will choose the one with the
    # lower running cost.
    AssetFactory(
        name="one",
        min_required_profit=1,
        running_cost_per_mw_hr=1,
        rates=tuple([RATE]),
    ),
    AssetFactory(
        name="two",
        min_required_profit=2,
        running_cost_per_mw_hr=2,
        rates=tuple([RATE]),
    )
]

RAMP_RATE_UP_ASSETS = [
    # Check that when given two assets it will choose the one with the
    # faster ramp rate up
    AssetFactory(
        name="one",
        min_required_profit=1,
        rates=tuple([RATE]),
    ),
    AssetFactory(
        name="two",
        min_required_profit=1,
        rates=tuple([RateFactory(
            ramp_up_import=2,
            ramp_up_export=2,
            ramp_down_import=1,
            ramp_down_export=1,
        )]),
    )
]

RAMP_RATE_DOWN_ASSETS = [
    # Check that when given two assets it will choose the one with the
    # faster ramp rate down
    AssetFactory(
        name="one",
        min_required_profit=1,
        rates=tuple([RATE]),
    ),
    AssetFactory(
        name="two",
        min_required_profit=1,
        rates=tuple([RateFactory(
            ramp_up_import=1,
            ramp_up_export=1,
            ramp_down_import=2,
            ramp_down_export=2,
        )]),
    )
]


VARIABLE_BOUNDS = [
    # Check that when an asset has a limited capacity
    # it will only be given to it's limit even if it
    # is the best choice
    AssetFactory(
        name="one",
        min_required_profit=1,
        capacity=4,
        rates=tuple([RATE]),
    ),
    AssetFactory(
        name="two",
        min_required_profit=1,
        capacity=6,
        rates=tuple([RATE]),
    )
]


MAXIMISE_FULFILLMENT = [
    # Check that when there is insufficient capacity the
    # power delivered is maximised.
    AssetFactory(
        name="one",
        min_required_profit=1,
        capacity=2,
        rates=tuple([RATE]),
    ),
    AssetFactory(
        name="two",
        min_required_profit=1,
        capacity=3,
        rates=tuple([RATE]),
    )
]


@pytest.mark.parametrize(
    "assets, asset_mw",
    [
        # Constraints
        # Necessary profit, fails
        (UNDER_MIN_REQUIRED_PROFIT, {"one": 0}),
        # Necessary profit, passes
        (OVER_MIN_REQUIRED_PROFIT, {"one": 10}),

        # Objective
        # Minimise Asset cost per mw
        (MINIMISE_COST_PER_MW, {"one": 10, "two": 0}),
        # Choose faster ramp rate
        (RAMP_RATE_UP_ASSETS, {"one": 0, "two": 10}),
        # Choose faster ramp down rate
        (RAMP_RATE_DOWN_ASSETS, {"one": 0, "two": 10}),

        # Variable bounds
        (VARIABLE_BOUNDS, {"one": 0, "two": 5}),
        # Maximise within bounds
        (MAXIMISE_FULFILLMENT, {"one": 0, "two": 0}),
    ],
    ids=[
        "1. Constraints: Necessary profit, fails",
        "2. Constraints: Necessary profit, passes",
        "3. Objective: Minimise Asset cost per mw",
        "4. Objective: Choose faster ramp rate",
        "5. Objective: Choose faster ramp down rate",
        "6. Variable bounds",
        "7. Maximise within bounds",
    ]
)
def test_run_engine(assets: Tuple[Asset], asset_mw: Dict[str, int]) -> None:

    boa = BOAFactory(
        mw=10,
        price_mw_hr=10,
        bmu__assets=tuple(assets),
        start=datetime(2020, 1, 1, 1),
        end=datetime(2020, 1, 1, 4),
    )
    candidates = [
        Candidate(
            asset=asset,
            boa=boa,
            mw=mw,
        )
        for asset in assets
        for mw in [0, 5, 10]
        if abs(mw) <= asset.capacity
    ]

    solution = run_engine(
        boa=boa,
        candidates=candidates,
    )

    assert len(solution.instructions) == len(asset_mw)

    for instruction in solution.instructions:
        assert asset_mw[instruction.asset.name] == instruction.mw
