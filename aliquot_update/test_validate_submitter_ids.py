from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from validate_submitter_ids import InputError, REQUIRED_COLUMNS, main, validate_submitter_ids


def write_tsv(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class ValidateSubmitterIdsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.input_path = self.root / "aliquots.tsv"
        self.log_path = self.root / "validation-errors.tsv"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_logs_invalid_submitter_ids_and_leaves_valid_ids_out(self) -> None:
        write_tsv(
            self.input_path,
            REQUIRED_COLUMNS,
            [
                {"submitter_id": "12345R000AK01"},
                {"submitter_id": "invalid"},
                {"submitter_id": "12345R999AK01"},
            ],
        )

        invalid_count = validate_submitter_ids(self.input_path, self.log_path)

        self.assertEqual(invalid_count, 2)
        with self.log_path.open(encoding="utf-8", newline="") as handle:
            entries = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(
            entries,
            [
                {
                    "submitter_id": "invalid",
                    "reason": "Code must be 13 characters long (got 7)",
                },
                {
                    "submitter_id": "12345R999AK01",
                    "reason": "Invalid RCT study day '999'. Must be one of "
                    "['000', '003', '007', '014', '028', '060', '090', '180']",
                },
            ],
        )

    def test_missing_required_column_fails(self) -> None:
        write_tsv(self.input_path, REQUIRED_COLUMNS[:-1], [])

        with self.assertRaisesRegex(InputError, "missing required columns"):
            validate_submitter_ids(self.input_path, self.log_path)

        self.assertFalse(self.log_path.exists())

    def test_input_and_log_must_be_different_files(self) -> None:
        write_tsv(self.input_path, REQUIRED_COLUMNS, [])

        with self.assertRaisesRegex(InputError, "must be different files"):
            validate_submitter_ids(self.input_path, self.input_path)

    def test_cli_writes_the_requested_log_file(self) -> None:
        write_tsv(self.input_path, REQUIRED_COLUMNS, [{"submitter_id": "invalid"}])

        result = main(["--input", str(self.input_path), "--log-file", str(self.log_path)])

        self.assertEqual(result, 0)
        self.assertTrue(self.log_path.is_file())


if __name__ == "__main__":
    unittest.main()
