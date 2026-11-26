import argparse
import random
import secrets
import sys
from pathlib import Path

from .check import validate_pairs
from .draw import DEFAULT_MAX_ATTEMPTS, TooManyAttemptsError, draw
from .models import DrawResult
from .reader import read_people, read_results
from .writer import write_results


def parse_args():
    parser = argparse.ArgumentParser(prog="secret_santa")
    subparsers = parser.add_subparsers(dest="command", required=True, help="[draw|check]")

    parser_draw = subparsers.add_parser("draw", help="draw giver - receiver pairs")
    parser_draw.add_argument("input_file", type=Path, help="input file path")
    parser_draw.add_argument("output_file", type=Path, help="output file path")
    parser_draw.add_argument("-n", "--no-mutual-pairs", action="store_true", help="forbidden A<->B pairs")
    parser_draw.add_argument("-s", "--seed", type=int, default=None, help="RNG seed")
    parser_draw.add_argument(
        "--max-attempts",
        type=int,
        default=DEFAULT_MAX_ATTEMPTS,
        help="max draw attempts (default: %(default)s)",
    )
    parser_draw.add_argument("-f", "--force", action="store_true", help="allow overwrite result file")

    parser_check = subparsers.add_parser("check", help="check if results in file are valid")
    parser_check.add_argument("people_file", type=Path, help="input people list")
    parser_check.add_argument("result_file", type=Path, help="draw result file")

    return parser.parse_args()


def cli():
    args = parse_args()
    try:
        if args.command == "draw":
            run_draw(
                input_file=args.input_file,
                output_file=args.output_file,
                seed=args.seed,
                no_mutual_pairs=args.no_mutual_pairs,
                max_attempts=args.max_attempts,
                force=args.force
            )
        elif args.command == "check":
            run_check(
                people_file=args.people_file,
                result_file=args.result_file
            )
    except (ValueError, TooManyAttemptsError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def run_draw(input_file, output_file, seed, no_mutual_pairs, max_attempts, force):

    if not force and output_file.is_file():
        raise ValueError(f"File: {output_file} exists! Use --force to overwrite")

    allow_mutual = not no_mutual_pairs

    if seed is None:
        seed = secrets.randbelow(2**32)
    rng = random.Random(seed)
    people = read_people(input_file)
    pairs = draw(people, rng, allow_mutual, max_attempts)
    result = DrawResult(pairs, seed, allow_mutual)

    write_results(output_file, result)
    print(f"Drew {len(pairs)} people, seed: {seed} → {output_file}")


def run_check(people_file, result_file):
    people = read_people(people_file)
    result = read_results(result_file, people)
    validate_pairs(people, result.pairs, result.allow_mutual)
    print("result file is valid")
