from datetime import datetime

import pytest

from tests.factories import AssetFactory, BOAFactory, InstructionFactory


@pytest.fixture
def asset() -> AssetFactory:
    return AssetFactory(
        id=1,
        name="asset",
        capacity=200,
        min_non_zero_time=10,
        min_zero_time=10,
        notice_to_deliver_bid=10,
        notice_to_deviate_from_zero=10,
        max_delivery_period=30,
        max_import_mw_hr=100,
        max_export_mw_hr=100,
    )


@pytest.fixture
def boa(asset: AssetFactory) -> BOAFactory:
    return BOAFactory(
        id=1,
        offer__bmu__assets={asset},
        start=datetime(2000, 1, 1, 10),
        end=datetime(2000, 1, 1, 10, 30),
        mw=500,
    )


@pytest.fixture
def previous_instruction(asset: AssetFactory) -> InstructionFactory:
    return InstructionFactory(
        id=1,
        asset=asset,
        start=datetime(2000, 1, 1, 5),
        end=datetime(2000, 1, 1, 5, 30),
    )


@pytest.fixture
def current_instruction(asset: AssetFactory) -> InstructionFactory:
    return InstructionFactory(
        id=2,
        asset=asset,
        start=datetime(2000, 1, 1, 9, 45),
        end=datetime(2000, 1, 1, 10, 15),
    )


@pytest.fixture
def future_instruction(asset: AssetFactory) -> InstructionFactory:
    return InstructionFactory(
        id=3,
        asset=asset,
        start=datetime(2000, 1, 1, 11, 30),
        end=datetime(2000, 1, 1, 12),
    )
