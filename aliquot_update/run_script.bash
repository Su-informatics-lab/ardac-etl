#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CATALOGS_PATH="/Users/jmccombs/projects/RDS/ardac/lab_biospecimen/AlcHepNet_Biosample_Files/Catalogs"
MANIFESTS_PATH="/Users/jmccombs/projects/RDS/ardac/lab_biospecimen/AlcHepNet_Biosample_Files/Distribution Manifests"
CURRENT_DATA_PATH="/Users/jmccombs/projects/RDS/ardac/ardac-etl/current_data/tsv"
CURRENT_TEMPLATES_PATH="/Users/jmccombs/projects/RDS/ardac/ardac-etl/current_dictionary/tsv"
STUDY="MMGE-NIAAA-ALCHEPNET"
CATALOG="${CATALOGS_PATH}/IB240019 (AHN) Specimen Catalog 09.01.2026 1.xlsx"
MANIFEST1="${MANIFESTS_PATH}/DIST3086_Simonetto_Manifest_For-Researcher_V01.xlsx"
MANIFEST2="${MANIFESTS_PATH}/DIST3087_Simonetto_Manifest_FOR-RESEARCHER_V01.xlsx"
ALIQUOTS="${CURRENT_DATA_PATH}/aliquot.tsv"
LABS="${CURRENT_DATA_PATH}/lab.tsv"
OUTPUT_TEMPLATE="${CURRENT_TEMPLATES_PATH}/submission_aliquot_template.tsv"
OUTPUT_PATH="/Users/jmccombs/projects/RDS/ardac/ardac-etl/aliquot_update/output"

COMMAND=(
    python "$SCRIPT_DIR/update_aliquot_distribution.py"
    --study "$STUDY"
    --catalog "$CATALOG"
    --manifest "$MANIFEST1" "$MANIFEST2"
    --aliquots "$ALIQUOTS"
    --labs "$LABS"
    --output-template "$OUTPUT_TEMPLATE"
    --output-dir "$OUTPUT_PATH"
)

printf '%q ' "${COMMAND[@]}"
printf '\n'
"${COMMAND[@]}"
