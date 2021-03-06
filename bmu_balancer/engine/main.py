import logging
import sys
from time import time
from typing import List

from pulp import LpMaximize, LpProblem, LpStatus

from bmu_balancer.engine.constraints import add_constraints
from bmu_balancer.engine.objective import set_objective
from bmu_balancer.engine.solution import get_solution
from bmu_balancer.engine.variables import create_variables
from bmu_balancer.models import BOA, Rate
from bmu_balancer.models.engine import Candidate, Solution
from bmu_balancer.operations.key_store import KeyStore

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def run_engine(
        boa: BOA,
        rates: KeyStore[Rate],
        candidates: List[Candidate],
) -> Solution:
    start = time()

    # Create model + formulate
    model = LpProblem("BMU-Balancer", LpMaximize)

    variables = create_variables(
        candidates=candidates,
    )
    set_objective(
        model=model,
        variables=variables,
        boa=boa,
        rates=rates,
    )
    add_constraints(
        model=model,
        variables=variables,
        boa=boa,
    )

    # Solve
    model.solve()
    log.info(f"Finished solving, got status {LpStatus[model.status]}. TOOK: {round(time() - start, 4)} secs.")

    # Get solution
    return get_solution(
        model=model,
        variables=variables,
    )
