import logging
import sys
from typing import Optional

import colorlog

from bmu_balancer.balance_a_bmu import balance_a_bmu

LOG_FORMAT = '%(log_color)s%(levelname)-7s | %(asctime)s | %(message)s'
LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'

colorlog.colorlog.default_log_colors = {
    'DEBUG': 'green',
    'WARNING': 'bold_yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def run(
        input_filepath: str,
        output_filepath: Optional[str] = None,
        log_level: str = logging.INFO,
        do_visualise: bool = True
) -> None:
    # Set-up logging
    colorlog.basicConfig(level=log_level, format=LOG_FORMAT, datefmt=LOG_DATEFMT, stream=sys.stderr)

    #  run
    balance_a_bmu(
        input_filepath=input_filepath,
        output_filepath=output_filepath,
        do_visualise=do_visualise,
    )


if __name__ == "__main__":
    run(*sys.argv[1:])
