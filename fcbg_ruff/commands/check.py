import argparse
from pprint import pprint

from ..check import validate_folder


def run() -> None:
    """Run check() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-check", description="check"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="path to the folder to validate.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        metavar="int",
        help="number of jobs running in parallel.",
        default=1,
    )
    args = parser.parse_args()
    violations = validate_folder(args.folder, args.jobs)
    pprint(violations)
