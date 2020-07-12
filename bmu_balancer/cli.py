import cProfile
import logging
import pstats
import sys
from typing import IO

import click
import colorlog

from bmu_balancer.run import run

colorlog.colorlog.default_log_colors = {
    'DEBUG': 'green',
    'WARNING': 'bold_yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def log_level(ctx, param, value):
    """Basic logging configuration."""
    log_format = '%(log_color)s%(levelname)-7s | %(asctime)s | %(message)s'
    colorlog.basicConfig(level=value, format=log_format, datefmt='%Y-%m-%dT%H:%M:%S', stream=sys.stderr)

    return value


@click.group()
@click.option(
    '--log',
    default='WARNING',
    callback=log_level,
    help='Set log level (ERROR/WARNING/INFO/DEBUG)')
def cli(log: str = logging.INFO):
    pass


load_file = click.argument('input_file', type=click.Path(),)


@cli.command(
    help='Run a full solve from json. Optional args, '
         '--output-file <OUTPUT_FILE> to save solution, '
         '--visualise boolean to turn off graphing.'
)
@load_file
@click.option('--output-file', default=None, type=click.Path(exists=False))
@click.option('--visualise', default=True, type=click.BOOL)
def solve(input_file: IO, output_file: IO, visualise: bool) -> None:
    run(input_filepath=input_file, output_filepath=output_file, visualise=visualise)


@cli.command(help='Run a solve and profile time to do so of called functions')
@load_file
@click.option('--num-solves', default=1, type=int)
def solve_and_profile(input_file: IO, num_solves: int) -> None:
    pr = cProfile.Profile()
    pr.enable()

    for i in range(num_solves):
        run(input_filepath=input_file, output_filepath=None, visualise=False)

    pr.disable()
    sortby = 'cumulative'
    ps = pstats.Stats(pr)
    ps.strip_dirs().sort_stats(sortby).print_stats()
