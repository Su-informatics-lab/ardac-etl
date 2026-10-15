#!/usr/bin/env python3
"""Validate biospecimen codes in an aliquot TSV."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import Sequence

from format_validators import validate_biospecimen_code


LOGGER = logging.getLogger("validate_submitter_ids")
REQUIRED_COLUMNS = (
    "type",
    "id",
    "project_id",
    "submitter_id",
    "aliquot_amount",
    "aliquot_collection_unit",
    "container_type",
    "specimen_type",
    "follow_ups.id",
    "follow_ups.submitter_id",
    "labs.id",
    "labs.submitter_id",
)


class InputError(ValueError):
    """Raised when the supplied TSV does not have the expected structure."""


def validate_submitter_ids(input_path: Path, log_path: Path) -> int:
    """Validate each aliquot submitter_id and write failures to a TSV log."""
    if not input_path.is_file():
        raise InputError(f"Input file does not exist: {input_path}")
    if input_path.resolve() == log_path.resolve():
        raise InputError("Input TSV and validation log must be different files")

    with input_path.open("r", encoding="utf-8-sig", newline="") as input_file:
        reader = csv.DictReader(input_file, delimiter="\t")
        if reader.fieldnames is None:
            raise InputError(f"Input file has no header: {input_path}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise InputError(f"Input file has duplicate column names: {input_path}")
        missing = sorted(set(REQUIRED_COLUMNS).difference(reader.fieldnames))
        if missing:
            raise InputError(
                f"Input file is missing required columns: {', '.join(missing)}"
            )

        invalid_count = 0
        with log_path.open("w", encoding="utf-8", newline="") as log_file:
            writer = csv.DictWriter(
                log_file,
                fieldnames=("submitter_id", "reason"),
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise InputError(
                        f"Input file has a row with the wrong number of fields "
                        f"at line {reader.line_num}"
                    )
                submitter_id = row["submitter_id"].strip()
                is_valid, reason = validate_biospecimen_code(submitter_id)
                if not is_valid:
                    writer.writerow({"submitter_id": submitter_id, "reason": reason})
                    invalid_count += 1

    LOGGER.info("Wrote %d invalid submitter_id values to %s", invalid_count, log_path)
    return invalid_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate aliquot submitter_id biospecimen codes."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input aliquot TSV")
    parser.add_argument(
        "--log-file", required=True, type=Path, help="TSV path for validation failures"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    try:
        validate_submitter_ids(args.input, args.log_file)
    except (InputError, OSError) as exc:
        LOGGER.error("%s", exc)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
