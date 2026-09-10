# Aliquot distribution updater

`update_aliquot_distribution.py` validates a biobank catalog, one or more
distribution manifests, and the current Gen3 aliquot and lab dumps. It writes
Gen3-ready aliquot updates plus one TSV report for each specified QC category.

## Run

Python 3.10 or newer and `openpyxl` are required. From the repository root:

```bash
python aliquot_update/update_aliquot_distribution.py \
  --study MMGE-NIAAA-ALCHEPNET \
  --catalog "/path/to/catalog.xlsx" \
  --manifest "/path/to/manifest-1.xlsx" "/path/to/manifest-2.xlsx" \
  --aliquots current_data/tsv/aliquot.tsv \
  --labs current_data/tsv/lab.tsv \
  --output-template current_dictionary/tsv/submission_aliquot_template.tsv \
  --output-dir /path/to/output
```

The output directory contains `updated_aliquot.tsv` with the exact headers from
the supplied submission template, along with:

- `missing_catalog_biospecimens.tsv`
- `extraeneous_collection_protocols.tsv` (name preserved from the specification)
- `missing_ardac_biospecimens.tsv`
- `redundant_manifest_records.tsv`
- `inconsistent_availability_status.tsv`

Every QC file is written even when it has no findings. A malformed input schema
or an unknown distribution protocol is a fatal error and is logged to stderr.

## Extending PI mappings

Add a source-to-Gen3 name pair to `PI_MAPPING` near the top of the script. The
program resolves that pair against the supplied lab dump instead of hard-coding
a Gen3 lab ID.
