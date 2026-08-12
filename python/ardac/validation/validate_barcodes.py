#!/usr/bin/env python3

import argparse
import pandas as pd
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Compare aliquot submitter_ids against biospecimen barcodes."
    )
    parser.add_argument(
        "--aliquots",
        required=True,
        help="Path to aliquot TSV file"
    )
    parser.add_argument(
        "--biospecimens",
        required=True,
        help="Path to biospecimen XLSX file"
    )
    parser.add_argument(
        "--biospecimens_earlier",
        required=True,
        help="Path to earlier biospecimen XLSX file"
    )
    parser.add_argument(
        "--extraneous_out",
        required=True,
        help="Path to write barcodes in the aliquots that are not found in either biospecimen catalog file (both XLSX files)"
    )
    parser.add_argument(
        "--missing_current_out",
        required=True,
        help="Path to write barcodes present in the current XLSX but missing from aliquots"
    )
    parser.add_argument(
        "--missing_earlier_out",
        required=True,
        help="Path to write barcodes present in the earlier XLSX but missing from aliquots"
    )

    args = parser.parse_args()

    # Read files
    aliquot_df = pd.read_csv(
        args.aliquots,
        sep="\t",
        dtype=str,
        keep_default_na=False
    )

    biospecimen_df = pd.read_excel(
        args.biospecimens,
        dtype=str,
        engine="openpyxl"
    )

    biospecimen_earlier_df = pd.read_excel(
        args.biospecimens_earlier,
        dtype=str,
        engine="openpyxl"
    )

    # Validate required columns
    if "submitter_id" not in aliquot_df.columns:
        sys.exit(
            f"ERROR: Column 'submitter_id' not found in TSV file."
        )

    if "Barcode" not in biospecimen_df.columns:
        sys.exit(
            f"ERROR: Column 'Barcode' not found in XLSX file."
        )

    if "Barcode" not in biospecimen_earlier_df.columns:
        sys.exit(
            f"ERROR: Column 'Barcode' not found in earlier XLSX file."
        )

    # Build sets of non-empty values
    tsv_ids = {
        str(x).strip()
        for x in aliquot_df["submitter_id"]
        if str(x).strip()
    }

    xlsx_barcodes = {
        str(x).strip()
        for x in biospecimen_df["Barcode"]
        if str(x).strip()
    }

    xlsx_earlier_barcodes = {
        str(x).strip()
        for x in biospecimen_earlier_df["Barcode"]
        if str(x).strip()
    }

    # Compute differences
    in_xlsx_not_tsv = sorted(xlsx_barcodes - tsv_ids)
    in_earlier_xlsx_not_tsv = sorted(xlsx_earlier_barcodes - tsv_ids)
    # Combined unique missing barcodes from both XLSX files
    extraneous = sorted(tsv_ids - (xlsx_barcodes | xlsx_earlier_barcodes))

    # Write combined missing barcodes (both XLSX files) to the provided txt file
    with open(args.extraneous_out, "w", newline="") as fh:
        fh.write(f"Barcodes in aliquot records (TSV) but not in biospecimen catalog files (XLSX): {len(extraneous)}\n");
        for b in extraneous:
            fh.write(f"{b}\n")

    # Write missing barcodes from the current XLSX
    with open(args.missing_current_out, "w", newline="") as fh:
        fh.write(f"Barcodes in current biospecimen catalog file (XLSX) but missing from ARDaC aliquot records (TSV): {len(in_xlsx_not_tsv)}\n")
        for b in in_xlsx_not_tsv:
            fh.write(f"{b}\n")

    # Write missing barcodes from the earlier XLSX
    with open(args.missing_earlier_out, "w", newline="") as fh:
        fh.write(f"Barcodes in earlier biospecimen catalog file (XLSX) but missing from ARDaC aliquot records (TSV): {len(in_earlier_xlsx_not_tsv)}\n")
        for b in in_earlier_xlsx_not_tsv:
            fh.write(f"{b}\n")


if __name__ == "__main__":
    main()
