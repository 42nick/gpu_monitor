import argparse
import sys
from time import sleep

from gpu_monitor.main import DESCRIPTION


def main(args: list[str]) -> None:
    """Run dummy script for testing."""
    parser = argparse.ArgumentParser(description="Dummy script for testing.")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")
    parser.add_argument("--error_at", type=int, default=4, help="Iteration to raise an error")
    args = parser.parse_args()

    for i in range(args.iterations):
        print("Hello, World!")
        if i == args.error_at:
            raise ValueError(DESCRIPTION)
        sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
