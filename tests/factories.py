from datetime import datetime, timedelta

from factory import Factory, List, LazyAttribute, SubFactory, fuzzy, Sequence

from bmu_balancer.models.inputs import Asset, Rate, AssetState, BMU, Offer
from bmu_balancer.models.outputs import Instruction

MIN, MAX = 0, 1000
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2030, 1, 1)
DEFAULT_MIN_DURATION = 30


# INPUTS --------------------------------------------------------------------- #

class AssetFactory(Factory):
    class Meta:
        model = Asset

    id = Sequence(lambda x: x)
    slug = LazyAttribute(lambda x: f"Asset {x.id}")
    capacity = 100
    running_cost_per_mw_hr = 0
    min_required_profit = fuzzy.FuzzyFloat(MIN, MAX)
    max_import_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    max_export_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    min_zero_time = fuzzy.FuzzyFloat(MIN, MAX)
    min_non_zero_time = fuzzy.FuzzyFloat(MIN, MAX)
    notice_to_deviate_from_zero = fuzzy.FuzzyFloat(MIN, MAX)
    max_delivery_period = fuzzy.FuzzyFloat(MIN, MAX)


class RateFactory(Factory):
    class Meta:
        model = Rate

    asset = SubFactory(AssetFactory)
    ramp_up_import = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_up_export = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_down_import = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_down_export = fuzzy.FuzzyFloat(MIN, MAX)
    min_mw = 0
    max_mw = None


class AssetStateFactory(Factory):
    class Meta:
        model = AssetState

    asset = SubFactory(AssetFactory)
    charge = fuzzy.FuzzyFloat(MIN, MAX)
    time = fuzzy.FuzzyDate(START_DATE, END_DATE)


class BMUFactory(Factory):
    class Meta:
        model = BMU

    id = Sequence(lambda x: x)
    assets = List([SubFactory(AssetFactory)])
    name = LazyAttribute(lambda x: f"Asset {x.id}")


class OfferFactory(Factory):
    class Meta:
        model = Offer

    bmu = SubFactory(BMUFactory)
    offer_start = fuzzy.FuzzyDate(START_DATE, END_DATE)
    offer_end = LazyAttribute(lambda x: x.start + timedelta(minutes=DEFAULT_MIN_DURATION))
    price_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    boa_start = None
    boa_end = None
    boa_value = None


# OUTPUTS -------------------------------------------------------------------- #


class InstructionFactory(Factory):
    class Meta:
        model = Instruction

    asset = SubFactory(AssetFactory)
    start = fuzzy.FuzzyDate(START_DATE, END_DATE)
    end = LazyAttribute(lambda c: c.start + timedelta(minutes=DEFAULT_MIN_DURATION))
    mw = fuzzy.FuzzyInteger(MIN, MAX)
    offer = SubFactory(OfferFactory)
