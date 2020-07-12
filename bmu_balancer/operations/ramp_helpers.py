from typing import Set


def get_ramp_up_start_time(rates: Set, mw: int) -> float:
    if len(rates) != 1:
        raise RuntimeError(
            f"{len(rates)} rates but only logic for one has been implemented!!")
    rate = rates[0]

    ramp_rate = rate.ramp_up_import if mw < 0 else rate.ramp_up_export
    return mw / float(ramp_rate)


def get_ramp_down_end_time(rates: Set, mw: int) -> float:
    if len(rates) != 1:
        raise RuntimeError(
            f"{len(rates)} rates but only logic for one has been implemented!!")
    rate = rates[0]

    ramp_rate = rate.ramp_down_export if mw < 0 else rate.ramp_down_export
    return mw / float(ramp_rate)
