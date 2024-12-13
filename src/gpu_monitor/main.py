"""Main module for the gpu monitor script."""

from __future__ import annotations

import argparse
import sys
from argparse import RawTextHelpFormatter
from math import inf
from pathlib import Path

from gpu_monitor.process_handler import DEFAULT_STORING_NAME, DEFAULT_STORING_ROOT, start_and_monitor


DEFAULT_LOG_LOCATION = DEFAULT_STORING_ROOT.joinpath(DEFAULT_STORING_NAME)
DESCRIPTION = f"""Start and monitor gpu and memory utilization of a process.
E.g. gpu-monitor 'python train.py'
Default log location: {DEFAULT_LOG_LOCATION}"""


def main(args: list[str] | None = None) -> int:
    """Entry point for the gpu monitor script."""
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser.add_argument("command", type=str, help="The command to run. E.g. 'python train.py'.")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Interval between checks in seconds.",
    )
    parser.add_argument(
        "--max_duration",
        type=float,
        default=inf,
        help="Maximum duration to run in seconds.",
    )
    parser.add_argument(
        "--storing_interval",
        type=int,
        default=10,
        help="Interval between storing data in seconds.",
    )
    parser.add_argument(
        "--log_location",
        type=Path,
        default=DEFAULT_LOG_LOCATION,
        help="Location to store the CSV file containing the gpu utilization. E.g. /path/to/log.csv.",
    )
    parser.add_argument(
        "--log_cpu_usage",
        action="store_true",
        help=(
            "Log CPU usage. Note: psutil is averaging the CPU usage over the interval.\n"
            "Therefore the script can not log within the exact interval."
        ),
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="If provided only the plot of the latest gpu util will be opened.",
    )
    args = parser.parse_args(args=args)

    if args.visualize:
        try:
            from gpu_monitor.visualize import visualize
        except ImportError as e:
            print(f"Error importing visualize: {e}")
            print(
                "Please install the package with visu extas e.g. pip install .[visu] or pip install gpu_monitor[visu].",
            )
            return 0

        visualize(args.log_location)

    return start_and_monitor(
        command=args.command,
        interval=args.interval,
        max_duration=args.max_duration,
        storing_interval=args.storing_interval,
        log_location=args.log_location,
        log_cpu_usage=args.log_cpu_usage,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
