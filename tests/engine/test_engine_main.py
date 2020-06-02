from datetime import datetime
from typing import Tuple, Dict

import pytest

from bmu_balancer.engine.main import run_engine
from bmu_balancer.models.engine import InstructionCandidate
from bmu_balancer.models.inputs import Asset
from bmu_balancer.utils import KeyStore
from tests.factories import AssetFactory, BOAFactory, RateFactory

UNDER_MIN_REQUIRED_PROFIT = [
    # Check that don't choose to turn on an asset if the
    # profit is less than the required profit to activate.
    # In this case;
    #      price_mw_hr * hours >= min_required_profit
    #        10             * 3     >= 10
    #  fails.
    AssetFactory(
        slug="one",
        min_required_profit=100,
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
        slug="one",
        min_required_profit=10,
    )
]

MINIMISE_COST_PER_MW = [
    # Check that when given two assets it will choose the one with the
    # lower running cost.
    AssetFactory(
        slug="one",
        min_required_profit=1,
        running_cost_per_mw_hr=1,
    ),
    AssetFactory(
        slug="two",
        min_required_profit=2,
        running_cost_per_mw_hr=2,
    )
]

RAMP_RATE_UP_ASSETS = [
    # Check that when given two assets it will choose the one with the
    # faster ramp rate up
    AssetFactory(
        slug="one",
        min_required_profit=1,
    ),
    AssetFactory(
        slug="two",
        min_required_profit=1,
    )
]
RAMP_RATE_UP = {
    "one": {"ramp_up_import": 1, "ramp_up_export": 1},
    "two": {"ramp_up_import": 2, "ramp_up_export": 2},
}

RAMP_RATE_DOWN_ASSETS = [
    # Check that when given two assets it will choose the one with the
    # faster ramp rate down
    AssetFactory(
        slug="one",
        min_required_profit=1,
    ),
    AssetFactory(
        slug="two",
        min_required_profit=1,
    )
]
RAMP_RATE_DOWN = {
    "one": {"ramp_down_import": 1, "ramp_down_export": 1},
    "two": {"ramp_down_import": 2, "ramp_down_export": 2},
}

VARIABLE_BOUNDS = [
    # Check that when an asset has a limited capacity
    # it will only be given to it's limit even if it
    # is the best choice
    AssetFactory(
        slug="one",
        min_required_profit=1,
        capacity=4,
    ),
    AssetFactory(
        slug="two",
        min_required_profit=1,
        capacity=6,
    )
]


MAXIMISE_FULFILLMENT = [
    # Check that when there is insufficient capacity the
    # power delivered is maximised.
    AssetFactory(
        slug="one",
        min_required_profit=1,
        capacity=2,
    ),
    AssetFactory(
        slug="two",
        min_required_profit=1,
        capacity=3,
    )
]


@pytest.mark.parametrize(
    "assets, ramp_rates, slug_mw",
    [
        # Constraints
        # Necessary profit, fails
        (UNDER_MIN_REQUIRED_PROFIT, {}, {"one": 0}),
        # Necessary profit, passes
        (OVER_MIN_REQUIRED_PROFIT, {}, {"one": 10}),

        # Objective
        # Minimise Asset cost per mw
        (MINIMISE_COST_PER_MW, {}, {"one": 10, "two": 0}),
        # Choose faster ramp rate
        (RAMP_RATE_UP_ASSETS, RAMP_RATE_UP, {"one": 0, "two": 10}),
        # # Choose faster ramp down rate
        (RAMP_RATE_DOWN_ASSETS, RAMP_RATE_DOWN, {"one": 0, "two": 10}),

        # Variable bounds
        (VARIABLE_BOUNDS, {}, {"one": 4, "two": 6}),
        # Maximise within bounds
        (MAXIMISE_FULFILLMENT, {}, {"one": 2, "two": 3}),
    ]
)
def test_run_engine(assets: Tuple[Asset], ramp_rates: Dict, slug_mw: Dict[str, int]) -> None:

    boa = BOAFactory(
        mw=10,
        offer__price_mw_hr=10,
        offer__bmu__assets=tuple(assets),
        start=datetime(2020, 1, 1, 1),
        end=datetime(2020, 1, 1, 4),
    )
    instruction_candidates = [
        InstructionCandidate(
            asset=asset,
            boa=boa,
            max_mw=asset.capacity,
        )
        for asset in assets
    ]
    rates = KeyStore(
        ['asset'],
        [
            RateFactory(asset=asset, **ramp_rates.get(asset.slug, {}))
            for asset in assets
        ]
    )

    solution = run_engine(
        boa=boa,
        rates=rates,
        instruction_candidates=instruction_candidates,
    )

    print("\n\nstatus: ", solution.status)
    print("objective: ", solution.objective)
    for instruction in solution.instructions:
        assert slug_mw[instruction.asset.slug] == instruction.mw
