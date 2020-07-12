from datetime import timedelta
from typing import Collection, Dict

import matplotlib.pyplot as plt
from matplotlib.dates import num2date

from bmu_balancer.models import Asset, BOA, Instruction
from bmu_balancer.models.engine import Candidate
from bmu_balancer.operations.key_store import KeyStore
from bmu_balancer.operations.ramp_helpers import get_ramp_down_end_time, get_ramp_up_start_time


def plot(
        boa: BOA,
        candidates: Dict[Asset, Candidate],
        instructions: KeyStore[Instruction],
) -> None:

    fig, axs = plt.subplots(1, len(boa.assets) + 1, sharex=True, sharey=True)

    for n, asset in enumerate(boa.assets):
        # Plot each asset candidate and the eventual choice against BOA
        plot_candidates(ax=axs[n], asset=asset, candidates=candidates[asset])
        plot_boa(ax=axs[n], boa=boa)
        plot_solution_instruction(ax=axs[n], asset=asset, instructions=instructions)
        graph_settings(ax=axs[n], title=asset.name)

    # Plot end result of cumulative choices
    n = len(boa.assets)
    plot_boa(ax=axs[n], boa=boa)
    plot_solution(ax=axs[n], boa=boa, instructions=instructions)
    graph_settings(ax=axs[n], title='Result')

    plt.show()


def plot_candidates(ax, asset: Asset, candidates: Collection[Candidate]) -> None:
    x, y = [], []
    for candidate in candidates:
        if candidate.mw != 0:
            # Start ramp-up
            ramp_up_start = get_ramp_up_start_time(rates=asset.rates, mw=candidate.mw)
            x.append(candidate.start - timedelta(hours=ramp_up_start))
            y.append(0)

            # Start BOA
            x.append(candidate.start)
            y.append(candidate.mw)

            # End BOA
            x.append(candidate.end)
            y.append(candidate.mw)

            # End ramp-down
            ramp_down_end = get_ramp_down_end_time(rates=asset.rates, mw=candidate.mw)
            x.append(candidate.end + timedelta(hours=ramp_down_end))
            y.append(0)

    ax.plot(x, y, color='blue', alpha=0.75, linewidth=0.5)


def plot_boa(ax, boa: BOA) -> None:
    ax.plot(
        [
            boa.ramp_start,
            boa.start,
            boa.end,
            boa.ramp_end,
        ],
        [0, boa.mw, boa.mw, 0],
        color='orange',
    )


def plot_solution_instruction(ax, asset: Asset, instructions: KeyStore[Instruction]) -> None:
    instruction = instructions.get_one_or_none(asset=asset)
    if instruction is not None:
        ramp_up_start = get_ramp_up_start_time(rates=asset.rates, mw=instruction.mw)
        ramp_down_end = get_ramp_down_end_time(rates=asset.rates, mw=instruction.mw)
        ax.fill_between(
            [
                instruction.start - timedelta(hours=ramp_up_start),
                instruction.start,
                instruction.end,
                instruction.end + timedelta(hours=ramp_down_end),
            ],
            [0, instruction.mw, instruction.mw, 0],
            facecolor='blue',
            alpha=0.5,
        )


def plot_solution(ax, boa: BOA, instructions: KeyStore[Instruction]) -> None:
    x, y = [], []

    levels = [0] + sorted([instr.mw for instr in instructions])

    # Cumulative Ramp-down
    counter = 0
    for level in levels:
        counter += level
        ramp_start = sum(
            get_ramp_up_start_time(rates=instr.asset.rates, mw=instr.mw)
            for instr in instructions
            if instr.mw > level
        )
        x.append(boa.start - timedelta(hours=ramp_start))
        y.append(counter)

    # Cumulative Ramp-up
    counter = sum(levels)
    for level in sorted(levels, reverse=True):
        ramp_end = sum(
            get_ramp_down_end_time(rates=instr.asset.rates, mw=instr.mw)
            for instr in instructions
            if instr.mw > level
        )
        x.append(boa.end + timedelta(hours=ramp_end))
        y.append(counter)
        counter -= level

    # Plot cumulative
    ax.fill_between(x, y, facecolor='orange', alpha=0.5)
    ax.plot(x, y, color='orange', alpha=0.75, linewidth=0.5)


def graph_settings(ax, title: str) -> None:
    ax.set_title(title)
    ax.set_ylabel('kW power')
    ax.set_xlabel('Time of day')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ticks = [
        '{:%H:%M}'.format(dt)
        for dt in num2date(ax.get_xticks())
    ]
    ax.set_xticklabels(ticks, rotation=90)
