from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from update_aliquot_distribution import (
    ALIQUOT_COLUMNS,
    CATALOG_COLUMNS,
    LAB_COLUMNS,
    MANIFEST_COLUMNS,
    InputError,
    update_aliquot_distribution,
)


TEMPLATE_COLUMNS = [
    "*type",
    "project_id",
    "*submitter_id",
    "*follow_ups.submitter_id",
    "labs.submitter_id",
    "aliquot_amount",
    "aliquot_collection_unit",
    "container_type",
    "specimen_type",
]


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def complete_row(columns: set[str], **values: str) -> dict[str, str]:
    row = {column: "" for column in columns}
    row.update(values)
    return row


class UpdateAliquotDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.catalog = self.root / "catalog.tsv"
        self.manifest = self.root / "manifest.tsv"
        self.aliquots = self.root / "aliquots.tsv"
        self.labs = self.root / "labs.tsv"
        self.template = self.root / "template.tsv"
        self.output = self.root / "output"

        lab_rows = [
            complete_row(
                LAB_COLUMNS,
                type="lab",
                submitter_id="lab_13",
                name_of_institute="Mayo Clinic Rochester",
                PI_name="Simonetto",
            ),
            complete_row(
                LAB_COLUMNS,
                type="lab",
                submitter_id="lab_0",
                name_of_institute="Not assigned",
                PI_name="Not assigned",
            ),
        ]
        write_tsv(self.labs, sorted(LAB_COLUMNS), lab_rows)
        write_tsv(self.template, TEMPLATE_COLUMNS, [])

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_generates_update_and_each_qc_category(self) -> None:
        catalog_rows = []
        for barcode in ("good", "extra", "missing-ardac", "redundant", "bad-status"):
            catalog_rows.append(
                complete_row(
                    CATALOG_COLUMNS,
                    Barcode=barcode,
                    **{
                        "Collection Protocol": "STUDY",
                        "Availability Status": "Distributed",
                        "Distribution Date": "01/09/2026 10:30",
                        "Distribution Protocol Short Title": "IB:Mayo Clinic:Douglas Simonetto",
                    },
                )
            )
        catalog_rows[-1]["Availability Status"] = "Available"
        write_tsv(self.catalog, sorted(CATALOG_COLUMNS), catalog_rows)

        manifest_rows = []
        for barcode in (
            "good",
            "missing-catalog",
            "extra",
            "missing-ardac",
            "redundant",
            "bad-status",
        ):
            manifest_rows.append(
                complete_row(
                    MANIFEST_COLUMNS,
                    **{
                        "Specimen Barcode": barcode,
                        "Collection Protocol Short Title": "STUDY",
                    },
                )
            )
        manifest_rows[2]["Collection Protocol Short Title"] = "OTHER-STUDY"
        write_tsv(self.manifest, sorted(MANIFEST_COLUMNS), manifest_rows)

        aliquot_rows = []
        for barcode in ("good", "extra", "redundant", "bad-status"):
            aliquot_rows.append(
                complete_row(
                    ALIQUOT_COLUMNS,
                    type="aliquot",
                    project_id="ARDaC-Test",
                    submitter_id=barcode,
                    **{
                        "follow_ups.submitter_id": f"follow-up-{barcode}",
                        "labs.submitter_id": "lab_0",
                        "specimen_type": "Serum",
                    },
                )
            )
        aliquot_rows[2]["labs.submitter_id"] = "lab_12"
        write_tsv(self.aliquots, sorted(ALIQUOT_COLUMNS), aliquot_rows)

        result = update_aliquot_distribution(
            study="STUDY",
            catalog_path=self.catalog,
            manifest_paths=[self.manifest],
            aliquot_path=self.aliquots,
            lab_path=self.labs,
            output_template_path=self.template,
            output_directory=self.output,
        )

        self.assertEqual(result.updated_count, 1)
        self.assertEqual(
            result.qc_counts,
            {
                "missing_catalog": 1,
                "extraneous_protocol": 1,
                "missing_ardac": 2,
                "redundant": 1,
                "inconsistent_availability": 1,
            },
        )
        with (self.output / "updated_aliquot.tsv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(list(rows[0]), TEMPLATE_COLUMNS)
        self.assertEqual(rows[0]["*submitter_id"], "good")
        self.assertEqual(rows[0]["labs.submitter_id"], "lab_13")
        self.assertNotIn("id", rows[0])

        expected_reports = {
            "missing_catalog_biospecimens.tsv": "missing-catalog",
            "extraeneous_collection_protocols.tsv": "extra",
            "redundant_manifest_records.tsv": "redundant",
            "inconsistent_availability_status.tsv": "bad-status",
        }
        for filename, barcode in expected_reports.items():
            with (self.output / filename).open(encoding="utf-8", newline="") as handle:
                report = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(report, [{"barcode": barcode}])

    def test_missing_required_column_fails_before_creating_output(self) -> None:
        write_tsv(self.catalog, ["Barcode"], [])
        write_tsv(self.manifest, sorted(MANIFEST_COLUMNS), [])
        write_tsv(self.aliquots, sorted(ALIQUOT_COLUMNS), [])

        with self.assertRaisesRegex(InputError, "missing required columns"):
            update_aliquot_distribution(
                study="STUDY",
                catalog_path=self.catalog,
                manifest_paths=[self.manifest],
                aliquot_path=self.aliquots,
                lab_path=self.labs,
                output_template_path=self.template,
                output_directory=self.output,
            )
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
