# Todo: Could this all be auto-generated off a dataclass?? Would be fun.
from datetime import datetime

from marshmallow import fields, post_load

from bmu_balancer.io.utils import PostLoadObjMixin
from bmu_balancer.models import Asset, AssetState, BMU, BOA, InputData, Instruction, Offer, Rate
from bmu_balancer.models.inputs import Parameters


class ParametersSchema(PostLoadObjMixin):

    __model__ = Parameters

    execution_time = fields.AwareDateTime(missing=datetime.utcnow())


class AssetSchema(PostLoadObjMixin):

    __model__ = Asset

    id = fields.Integer(required=True)
    name = fields.String(missing=None)
    capacity = fields.Float(required=True)
    running_cost_per_mw_hr = fields.Float(missing=0)
    min_required_profit = fields.Float(missing=0)
    max_import_mw_hr = fields.Float(missing=0)
    max_export_mw_hr = fields.Float(missing=0)
    single_import_mw_hr = fields.Float(missing=None, nullable=True)
    single_export_mw_hr = fields.Float(missing=None, nullable=True)
    min_zero_time = fields.Float(missing=0)
    min_non_zero_time = fields.Float(missing=0)
    notice_to_deviate_from_zero = fields.Float(missing=0)
    notice_to_deliver_bid = fields.Float(missing=0, nullable=False)
    max_delivery_period = fields.Float(missing=None)


class RateSchema(PostLoadObjMixin):

    __model__ = Rate

    id = fields.Integer(required=True)
    asset = fields.Function(deserialize=lambda data, context: context['assets'][data])
    ramp_up_import = fields.Float(required=True)
    ramp_up_export = fields.Float(required=True)
    ramp_down_import = fields.Float(required=True)
    ramp_down_export = fields.Float(required=True)
    min_mw = fields.Integer(missing=0)
    max_mw = fields.Integer(missing=None)


class AssetStateSchema(PostLoadObjMixin):

    __model__ = AssetState

    id = fields.Integer(required=True)
    asset = fields.Function(deserialize=lambda data, context: context['assets'][data])
    start = fields.AwareDateTime(required=True)
    end = fields.AwareDateTime(required=True)
    charge = fields.Float(missing=0)
    available = fields.Boolean(missing=False)


class BMUSchema(PostLoadObjMixin):

    __model__ = BMU

    id = fields.Integer(required=True)
    name = fields.String(missing=None)
    assets = fields.List(fields.Function(deserialize=lambda data, context: context['assets'][data]))

    @post_load
    def list_to_tuple_for_immutability(self, data, **kwargs):
        data['assets'] = tuple(data.get('assets', []))
        return data


class OfferSchema(PostLoadObjMixin):

    __model__ = Offer

    id = fields.Integer(required=True)
    bmu = fields.Function(deserialize=lambda data, context: context['bmus'][data])
    start = fields.AwareDateTime(nullable=True, missing=None)
    end = fields.AwareDateTime(nullable=True, missing=None)
    price_mw_hr = fields.Float(missing=0)


class InstructionSchema(PostLoadObjMixin):

    __model__ = Instruction

    id = fields.Integer(required=True)
    asset = fields.Function(deserialize=lambda data, context: context['assets'][data])
    mw = fields.Float(required=True)
    start = fields.AwareDateTime(required=True)
    end = fields.AwareDateTime(required=True)
    boa = fields.Function(deserialize=lambda data, context: context['boa'][data])


class BOASchema(PostLoadObjMixin):

    __model__ = BOA

    id = fields.Integer(required=True)
    start = fields.AwareDateTime(required=True)
    end = fields.AwareDateTime(required=True)
    mw = fields.Float(required=True)
    offer = fields.Function(deserialize=lambda data, context: context['offers'][data])


class InputDataSchema(PostLoadObjMixin):

    __model__ = InputData

    parameters = fields.Nested(ParametersSchema)
    assets = fields.List(fields.Function(deserialize=lambda data, context: context['assets'][data['id']]))
    rates = fields.List(fields.Function(deserialize=lambda data, context: context['rates'][data['id']]))
    states = fields.List(fields.Function(deserialize=lambda data, context: context['states'][data['id']]))
    bmus = fields.List(fields.Function(deserialize=lambda data, context: context['bmus'][data['id']]))
    offers = fields.List(fields.Function(deserialize=lambda data, context: context['offers'][data['id']]))
    instructions = fields.List(fields.Function(deserialize=lambda data, context: context['instructions'][data['id']]))
    boa = fields.Nested(BOASchema)
