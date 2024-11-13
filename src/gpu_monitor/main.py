"""Main module for the gpu monitor script."""

import argparse
from math import inf
from pathlib import Path

from gpu_monitor.process_handler import DEFAULT_STORING_NAME, DEFAULT_STORING_ROOT, start_and_monitor


def main() -> None:
    """Entry point for the gpu monitor script."""
    parser = argparse.ArgumentParser(description="Start and monitor a process.")
    parser.add_argument("command", type=str, help="The command to run.")
    parser.add_argument("--interval", type=int, default=1, help="Interval between checks in seconds.")
    parser.add_argument("--max_duration", type=int, default=inf, help="Maximum duration to run in seconds.")
    parser.add_argument("--storing_interval", type=int, default=10, help="Interval between storing data in seconds.")
    parser.add_argument(
        "--log_location",
        type=Path,
        default=DEFAULT_STORING_ROOT.joinpath(DEFAULT_STORING_NAME),
        help="Location to store the CSV file containing the gpu utilization.",
    )
    parser.add_argument("--log_cpu_usage", action="store_true", help="Log CPU usage.")
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="If provided only the plot of the latest gpu util will be opened.",
    )
    args = parser.parse_args()

    if args.visualize:
        try:
            from gpu_monitor.visualize import visualize
        except ImportError as e:
            print(f"Error importing visualize: {e}")
            print(
                "Please install the package with visu extas e.g. pip install .[visu] or pip install gpu_monitor[visu].",
            )
            return

        visualize(args.log_location)

    start_and_monitor(
        command=args.command,
        interval=args.interval,
        max_duration=args.max_duration,
        storing_interval=args.storing_interval,
        log_location=args.log_location,
        log_cpu_usage=args.log_cpu_usage,
    )


if __name__ == "__main__":
    main()
