"""Main module for the gpu monitor script."""

import argparse
from math import inf

from gpu_monitor.process_handler import start_and_monitor


def main() -> None:
    """Entry point for the gpu monitor script."""
    parser = argparse.ArgumentParser(description="Start and monitor a process.")
    parser.add_argument("command", type=str, help="The command to run.")
    parser.add_argument("--interval", type=int, default=1, help="Interval between checks in seconds.")
    parser.add_argument("--max_duration", type=int, default=inf, help="Maximum duration to run in seconds.")
    parser.add_argument("--storing_interval", type=int, default=10, help="Interval between storing data in seconds.")
    parser.add_argument(
        "--storing_location",
        type=str,
        default=".vscode/process_info.csv",
        help="Location to store the CSV file.",
    )
    parser.add_argument("--log_cpu_usage", action="store_true", help="Log CPU usage.")
    args = parser.parse_args()
    start_and_monitor(
        command=args.command,
        interval=args.interval,
        max_duration=args.max_duration,
        storing_interval=args.storing_interval,
        storing_location=args.storing_location,
        log_cpu_usage=args.log_cpu_usage,
    )


if __name__ == "__main__":
    main()
