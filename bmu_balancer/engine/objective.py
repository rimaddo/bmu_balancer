from datetime import timedelta
from typing import Tuple

from pulp import LpProblem

from bmu_balancer.models import BOA
from bmu_balancer.models.engine import Assignment, Variables
from bmu_balancer.operations.instruction_helpers import get_instruction_cost
from bmu_balancer.operations.pre_solve.get_mw_bounds import SECS_IN_HR
from bmu_balancer.operations.ramp_helpers import get_ramp_down_end_time, get_ramp_up_start_time


def set_objective(model: LpProblem, variables: Variables, boa: BOA) -> None:
    model += sum(
        var * (
            # Asset production of power
            sum(
                # Profit
                boa.price_mw_hr * candidate.hours * candidate.mw
                # Cost
                - get_instruction_cost(instruction=candidate)
                for candidate in assignment.candidates
            )
            # Profile penalty for imbalance over + under
            - get_imbalance_penalty(assignment=assignment, boa=boa)
        )
        for assignment, var in variables.assignments.items()
    )


def get_imbalance_penalty(assignment: Assignment, boa: BOA) -> float:
    over, under = get_profile_over_under(assignment=assignment, boa=boa)
    if under != 0:
        print("over, under", over, under)
    return over + under * 1


def get_profile_over_under(assignment: Assignment, boa: BOA) -> Tuple[float, float]:
    over_total, under_total = 0, 0

    levels = [0] + sorted([candidate.mw for candidate in assignment.candidates])

    # Cumulative Ramp-down
    counter = 0
    bmu_ceil_length = None
    for level in levels:

        # Calculate base, otherwise the base will be the ceil from last iteration
        bmu_base_length = (
            get_bmu_duration(assignment=assignment, boa=boa, level=level)
            if bmu_ceil_length is None
            else bmu_ceil_length
        )
        boa_base_length = get_boa_duration(assignment=assignment, boa=boa, level=level)

        # Calculate ceil
        counter += level
        bmu_ceil_length = get_bmu_duration(assignment=assignment, boa=boa, level=level)
        boa_ceil_length = get_boa_duration(assignment=assignment, boa=boa, level=level)

        # Calculate total area
        bmu_area = area_of_a_trapezoid(
            base_length=bmu_base_length,
            ceil_length=bmu_ceil_length,
            height=level,
        )
        boa_area = area_of_a_trapezoid(
            base_length=boa_base_length,
            ceil_length=boa_ceil_length,
            height=level,
        )
        over_total += max(bmu_area - boa_area, 0)
        under_total -= min(bmu_area - boa_area, 0)

    return over_total, under_total


def get_bmu_duration(assignment: Assignment, boa: BOA, level: float) -> float:
    ramp_start_offset = sum(
        get_ramp_up_start_time(rates=candidate.asset.rates, mw=candidate.mw)
        for candidate in assignment.candidates
        if candidate.mw > level
    )
    ramp_start = boa.start - timedelta(hours=ramp_start_offset)

    ramp_end_offset = sum(
        get_ramp_down_end_time(rates=candidate.asset.rates, mw=candidate.mw)
        for candidate in assignment.candidates
        if candidate.mw > level
    )
    ramp_end = boa.end + timedelta(hours=ramp_end_offset)

    return (ramp_end - ramp_start).total_seconds() / SECS_IN_HR


def get_boa_duration(assignment: Assignment, boa: BOA, level: float) -> float:
    ramp_start_offset = get_ramp_up_start_time(rates=boa.rates, mw=level)
    ramp_start = boa.start - timedelta(hours=ramp_start_offset)

    ramp_end_offset = get_ramp_down_end_time(rates=boa.rates, mw=level)
    ramp_end = boa.end + timedelta(hours=ramp_end_offset)

    return (ramp_end - ramp_start).total_seconds() / SECS_IN_HR


def area_of_a_trapezoid(base_length: float, ceil_length: float, height: float) -> float:
    return (
        base_length + ceil_length
    ) * 0.5 * height
