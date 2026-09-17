import argparse
import errno
import logging
import os
import sys
from pathlib import Path

import pandas as pd

import _constants


def generate_observational_case_node(
    obs_subjects_path: Path,
    template_headers: list[str],
    obs_aki_path: Path | None = None,
) -> pd.DataFrame:
    """Generate an ARDaC case node from observational subject data."""
    logger.info("Reading observational subjects file: %s", obs_subjects_path.as_posix())
    df_input = pd.read_csv(obs_subjects_path.as_posix(), sep=",", dtype=str)
    df_input = df_input[df_input["usubjid"] != "31014"]
    logger.info("Done reading observational subjects file")

    df_output = pd.DataFrame(index=df_input.index, columns=template_headers)
    df_output.loc[:, "*type"] = "case"
    df_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
    df_output.loc[:, "*studies.submitter_id"] = "obs"
    df_output.loc[:, "index_date"] = "Study Enrollment"
    df_output["*submitter_id"] = df_input["usubjid"].apply(
        lambda value: f"{value}_obs" if pd.notna(value) else None
    )
    df_output["cohort"] = df_input["obs_arm"].apply(
        lambda value: value.split(":")[-1].strip() if pd.notna(value) else None
    )
    df_output["study_site"] = df_input["site"].apply(
        lambda value: value.strip() if pd.notna(value) else None
    )
    df_output["vital_status"] = df_input["ALIVE"].apply(
        lambda value: "alive" if value == "Y" else "dead" if value == "N" else None
    )

    if obs_aki_path is not None:
        logger.info("Reading observational AKI file: %s", obs_aki_path.as_posix())
        df_aki = pd.read_csv(obs_aki_path.as_posix(), sep=",", dtype=str)
        aki_map = df_aki.set_index("usubjid")["akiaernyn"].fillna("Unknown").to_dict()
        df_output["aki_status"] = df_input["usubjid"].apply(
            lambda value: aki_map.get(value, "Unknown")
        )

    return df_output


def generate_clinical_case_node(
    rct_subjects_path: Path,
    template_headers: list[str],
    rct_aki_path: Path | None = None,
) -> pd.DataFrame:
    """Generate an ARDaC case node from clinical subject data."""
    logger.info("Reading clinical subjects file: %s", rct_subjects_path.as_posix())
    df_input = pd.read_csv(rct_subjects_path.as_posix(), sep=",", dtype=str)
    logger.info("Done reading clinical subjects file")

    df_output = pd.DataFrame(index=df_input.index, columns=template_headers)
    df_output.loc[:, "*type"] = "case"
    df_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
    df_output.loc[:, "*studies.submitter_id"] = "clinical"
    df_output.loc[:, "index_date"] = "Study Enrollment"
    df_output["*submitter_id"] = df_input["usubjid"].apply(
        lambda value: f"{value}_clinical" if pd.notna(value) else None
    )
    df_output["actarm"] = df_input["rct_arm"].apply(
        lambda value: value.strip() if pd.notna(value) else None
    )
    df_output["rct_meld_strata"] = df_input["rct_meld_strata"].apply(
        lambda value: value.strip() if pd.notna(value) else None
    )
    df_output["study_site"] = df_input["site"].apply(
        lambda value: value.strip() if pd.notna(value) else None
    )
    df_output["vital_status"] = df_input["ALIVE"].apply(
        lambda value: "alive" if value == "Y" else "dead" if value == "N" else None
    )

    if rct_aki_path is not None:
        logger.info("Reading clinical AKI file: %s", rct_aki_path.as_posix())
        df_adverse_events = pd.read_csv(rct_aki_path.as_posix(), sep=",", dtype=str)
        aki_patients = set(
            df_adverse_events.loc[
                df_adverse_events["ae_aki_indicator"] == "1", "usubjid"
            ]
        )
        df_output["aki_status"] = df_input["usubjid"].apply(
            lambda value: "Yes" if value in aki_patients else "No"
        )

    mapped_columns = {
        "*type", "project_id", "*submitter_id", "*studies.submitter_id",
        "actarm", "rct_meld_strata", "study_site", "vital_status",
        "index_date", "aki_status",
    }
    for column in df_output.columns:
        if column not in mapped_columns:
            df_output[column] = None

    return df_output


def main(command_arguments: argparse.Namespace) -> int:
    template_path = Path(command_arguments.nodeTemplatesPath, _constants.CASE_TEMPLATE_FILE_NAME)
    subjects_path = Path(command_arguments.dccSubjectsFile)
    node_output_path = Path(command_arguments.nodeOutputPath)
    aki_path = Path(command_arguments.dccAkiFile) if command_arguments.dccAkiFile else None

    if not template_path.is_file():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path)
    if not subjects_path.is_file():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), subjects_path)
    if aki_path is not None and not aki_path.is_file():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), aki_path)
    if not node_output_path.is_dir():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), node_output_path)

    template_headers = pd.read_csv(template_path.as_posix(), sep="\t", nrows=0).columns.tolist()
    if command_arguments.subjectsType == "observational":
        output_path = node_output_path / _constants.CASE_OBS_FILE_NAME
        output = generate_observational_case_node(subjects_path, template_headers, aki_path)
    elif command_arguments.subjectsType == "clinical":
        output_path = node_output_path / _constants.CASE_RCT_FILE_NAME
        output = generate_clinical_case_node(subjects_path, template_headers, aki_path)
    else:
        raise ValueError(
            f"Processing for subjects_type={command_arguments.subjectsType} is not implemented"
        )

    output.to_csv(output_path.as_posix(), sep="\t", index=False, header=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ARDaC case nodes from DCC subject data.")
    valid_log_level_names = logging.getLevelNamesMapping()
    valid_log_level_names.pop("NOTSET")
    parser.add_argument(
        "--version", action="version",
        version=f"DCC_VERSION={_constants.DCC_RELEASE_STRING},MAPPING_VERSION={_constants.MAPPING_VERSION_STRING}",
    )
    parser.add_argument("--dcc_version", action="version", version=_constants.DCC_RELEASE_STRING)
    parser.add_argument("--mapping_version", action="version", version=_constants.MAPPING_VERSION_STRING)
    parser.add_argument("--log_level", dest="logLevel", default="INFO", choices=list(valid_log_level_names.keys()))
    parser.add_argument("--node_templates_path", dest="nodeTemplatesPath", required=True)
    parser.add_argument("--subjects_type", dest="subjectsType", required=True, choices=["observational", "clinical"])
    parser.add_argument("--dcc_subjects_file", dest="dccSubjectsFile", required=True)
    parser.add_argument("--dcc_aki_file", dest="dccAkiFile", help="Path to the observational AKI or clinical adverse events CSV file")
    parser.add_argument("--node_output_path", dest="nodeOutputPath", required=True)
    parsed_args = parser.parse_args()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(parsed_args.logLevel)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.basicConfig(level=parsed_args.logLevel, handlers=[console_handler])
    logger = logging.getLogger(parser.prog)
    logger.setLevel(parsed_args.logLevel)

    status = 3
    try:
        status = main(parsed_args)
    except FileNotFoundError as error:
        logger.critical("Input file not found: %s", error.filename)
    except ValueError as error:
        logger.critical("Command line argument or parameter had a bad value: %s", error)
    except Exception:
        logger.critical("Caught an exception", exc_info=True)
    raise SystemExit(status)
