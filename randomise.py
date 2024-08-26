#!/usr/bin/env python3
"""
Generate Thunderstone Quest Scenarios

Call with -h for details.
"""
__author__ = "Steve Campbell"

# Standard library imports
from argparse import ArgumentParser, RawTextHelpFormatter, Namespace as CliArgs
import yaml
import os
import sys

# Third Party Modules

# Local imports

# Constants



def main():
    """Main part of script"""

    # Handle our CLI arguments and provide -h (help) text
    parser = ArgumentParser(description=f"""
Generate Thunderstone Quest scenarios.
""",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="debug level output")
    parser.add_argument("-v", "--verbose", action="store_true", help="show what we're doing")
    parser.add_argument("-n", "--dry-run", action="store_true", help="show data"),
    parser.add_argument("--max-count", type=int, help="Specify the type for non-boolean params"),
    parser.add_argument("pos_arg1", help="help for positional argument")
    args = parser.parse_args()
    validate_args(args)

    # Application code starts here.
    if args.dry_run:
        # For testing
        print(json.dumps({"Sy": sy}))


def validate_args(args: CliArgs) -> None:
    if not args.foo:
        sys.exit("Some invalid argument specified! Use -h for help.")


if __name__ == "__main__":
    main()


