import json
from datetime import date, datetime
from typing import Dict, List

from bmu_balancer.io.input_schemas import (
    AssetSchema, AssetStateSchema,
    BMUSchema,
    InputDataSchema,
    InstructionSchema,
    OfferSchema,
    RateSchema,
)
from bmu_balancer.io.output_schemas import SolutionSchema
from bmu_balancer.models import InputData
from bmu_balancer.models.engine import Solution

JSON_SUFFIX = ".json"


def load_input_data(filepath: str) -> InputData:
    """Given a file, load the data in it into an input object.
    Todo: Would be nice for this to be able to take excel.
    """
    data_dict = load_json(filepath)

    context = {}
    for name, schema in {
        'assets': AssetSchema,
        'rates': RateSchema,
        'states': AssetStateSchema,
        'bmus': BMUSchema,
        'offers': OfferSchema,
        'instructions': InstructionSchema
    }.items():
        items = schema(context=context).load(data_dict[name], many=True)
        context.update({name: {item.id: item for item in items}})

    return InputDataSchema(context=context).load(data_dict)


def dump_solution(filepath: str, solution: Solution) -> None:
    data = SolutionSchema(strict=True).dump(solution).data
    dump_json(filepath=filepath, data=data)


def load_json(filepath: str) -> Dict:
    if JSON_SUFFIX not in filepath:
        raise RuntimeError(f"Can currently only handle excel, got {filepath}")

    with open(filepath) as file:
        return json.load(file)


def dump_json(filepath: str, data: Dict) -> None:
    if JSON_SUFFIX not in filepath:
        raise RuntimeError(f"Can currently only handle excel, got {filepath}")

    with open(filepath, 'w') as file:
        json.dump(data, file, default=json_serial)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.date().isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))