from pulp import LpProblem

from bmu_balancer.models.engine import Variables, InstructionCandidate
from bmu_balancer.models.inputs import Offer, BOA, Rate
from bmu_balancer.utils import KeyStore, get_item_at_time

PRICE_GROUP_SCALER = 10
RAMP_RATE_SCALER = 10


def set_objective(model: LpProblem, variables: Variables, boa: BOA, rates: KeyStore[Rate]) -> None:
    model += sum(
        var * (
            # Earn power cost
            boa.price_mw_hr
            # Asset cost per mw (minimise cost to run)
            - candidate.asset.running_cost_per_mw_hr * candidate.hours
            # Penalty for the amount that you under-deliver in ramp up
            - 1 / float(get_ramp_rate_penalty(boa=boa, candidate=candidate, rates=rates, up=True))
            # Penalty for the amount that you under-deliver in ramp down
            - 1 / float(get_ramp_rate_penalty(boa=boa, candidate=candidate, rates=rates, up=False))
        )
        for candidate, var in variables.instruction_candidates.items()
    )


def get_ramp_rate_penalty(boa: BOA, candidate: InstructionCandidate, rates: KeyStore[Rate], up: bool = True) -> float:
    """This is just a vary hacky first step to get something running way to do this,
    will calculate exactly in the future and with multiple rates."""
    rate = rates.get_one_or_none(asset=candidate.asset)
    if rate is None:
        raise RuntimeError(f"Missing rate for asset {candidate.asset}")
    if up:
        return getattr(rate, 'ramp_up_import') if boa.is_import else getattr(rate, 'ramp_up_export')
    return getattr(rate, 'ramp_down_import') if boa.is_import else getattr(rate, 'ramp_down_export')
