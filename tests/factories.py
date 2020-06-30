from datetime import datetime, timedelta

from factory import Factory, LazyAttribute, List, Sequence, SubFactory, fuzzy

from bmu_balancer.models.inputs import Asset, BMU, BOA, Rate, State
from bmu_balancer.models.outputs import Instruction

MIN, MAX = 0, 1000
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2030, 1, 1)
DEFAULT_MIN_DURATION = 30


# INPUTS --------------------------------------------------------------------- #

class RateFactory(Factory):
    class Meta:
        model = Rate

    id = Sequence(lambda x: x)
    ramp_up_import = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_up_export = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_down_import = fuzzy.FuzzyFloat(MIN, MAX)
    ramp_down_export = fuzzy.FuzzyFloat(MIN, MAX)
    min_mw = 0
    max_mw = None


class AssetFactory(Factory):
    class Meta:
        model = Asset

    id = Sequence(lambda x: x)
    name = LazyAttribute(lambda x: f"Asset {x.id}")
    capacity = 100
    running_cost_per_mw_hr = 0
    min_required_profit = fuzzy.FuzzyFloat(MIN, MAX)
    max_import_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    max_export_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    single_import_mw_hr = None
    single_export_mw_hr = None
    min_zero_time = fuzzy.FuzzyFloat(MIN, MAX)
    min_non_zero_time = fuzzy.FuzzyFloat(MIN, MAX)
    notice_to_deviate_from_zero = fuzzy.FuzzyFloat(MIN, MAX)
    notice_to_deliver_bid = fuzzy.FuzzyFloat(MIN, MAX)
    max_delivery_period = fuzzy.FuzzyFloat(MIN, MAX)
    rates = List([SubFactory(RateFactory)])


class StateFactory(Factory):
    class Meta:
        model = State

    id = Sequence(lambda x: x)
    asset = SubFactory(AssetFactory)
    start = fuzzy.FuzzyDate(START_DATE, END_DATE)
    end = LazyAttribute(lambda x: x.start + timedelta(minutes=DEFAULT_MIN_DURATION))
    available = True
    charge = fuzzy.FuzzyFloat(MIN, MAX)


class BMUFactory(Factory):
    class Meta:
        model = BMU

    id = Sequence(lambda x: x)
    assets = List([SubFactory(AssetFactory)])
    name = LazyAttribute(lambda x: f"Asset {x.id}")


class BOAFactory(Factory):
    class Meta:
        model = BOA

    id = Sequence(lambda x: x)
    start = fuzzy.FuzzyDate(START_DATE, END_DATE)
    end = LazyAttribute(lambda x: x.start + timedelta(minutes=DEFAULT_MIN_DURATION))
    mw = fuzzy.FuzzyFloat(MIN, MAX)
    price_mw_hr = fuzzy.FuzzyFloat(MIN, MAX)
    bmu = SubFactory(BMUFactory)


# OUTPUTS -------------------------------------------------------------------- #


class InstructionFactory(Factory):
    class Meta:
        model = Instruction

    id = Sequence(lambda x: x)
    asset = SubFactory(AssetFactory)
    start = fuzzy.FuzzyDate(START_DATE, END_DATE)
    end = LazyAttribute(lambda c: c.start + timedelta(minutes=DEFAULT_MIN_DURATION))
    mw = fuzzy.FuzzyInteger(MIN, MAX)
    boa = SubFactory(BOAFactory)
