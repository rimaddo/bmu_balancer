import logging
import sys
from typing import IO

import click
import colorlog

from bmu_balancer.run import run, run_all_levels

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
write_output = click.argument('output_file', type=click.Path(),)


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


@cli.command(
    help='Run a full solve from json. Optional args, '
         '--output-folder <OUTPUT_FOLDER> to save all solutions, '
         '--visualise boolean to turn off graphing.'
)
@load_file
@click.option('--output-folder', default=None, type=click.Path(exists=False))
@click.option('--visualise', default=True, type=click.BOOL)
def solve_all_levels(input_file: IO, output_folder: IO, visualise: bool) -> None:
    run_all_levels(input_filepath=input_file, output_folder=output_folder, visualise=visualise)
