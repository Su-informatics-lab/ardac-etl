import argparse
from argparse import Namespace
import json
import logging
import sys
from gen3.submission import Gen3Submission
from gen3.auth import Gen3Auth

def main(parsed_args: Namespace, submission: Gen3Submission) -> int:
    if parsed_args.json_file is None:
        raise ValueError(f'--json-file must be set')
    
    with open(parsed_args.json_file, "r") as json_file:
        json_obj = json.load(json_file)

    logger.info(f'JSON read from file is: {json_obj}')
    # This method will throw an exception upon error
    submission.create_project(parsed_args.program_name, json_obj)

    return 0
    

if __name__ == "__main__":
    status = 3
    parser = argparse.ArgumentParser(
        description="""This utility creates new projects within a Gen3 instance.  A program name and a JSON file containing the definition of the new project are required""",
        epilog="""The format of the JSON project definition is:
            {
                "type": "project",
                "availability_type": "<availability_type>",
                "code": "<code_string>",
                "dbgap_accession_number": "<dbgap_accession_number>",
                "investigator_affiliation": "<investigator_affiliation>",
                "investigator_name": "<investigator_name>",
                "name": "<project_name>"
            }
            The \'programs\' fields are not permitted in the JSON definition See the project node specification for more details."""
    )

    valid_log_level_names_mapping = logging.getLevelNamesMapping()
    valid_log_level_names_mapping.pop("NOTSET")
    parser.add_argument(
        "--log_level",
        dest="log_level",
        default="INFO",
        choices=list(valid_log_level_names_mapping.keys()),
        help="A standard log level from the Python logger package"
    )
    parser.add_argument(
        "--commons-url",
        dest="commons_url",
        required=True,
        help="The URL of the Gen3 data commons to access"
    )
    parser.add_argument(
        "--program-name",
        dest="program_name",
        required=True,
        help="The project name from which the node data will be deleted"
    )
    parser.add_argument(
        "--json-file",
        dest="json_file",
        required=True,
        help="Path to file containing a JSON record defining the project instance to create"
    )
    parser.add_argument(
        "--api-key-file",
        dest="api_key_file",
        required=True,
        help="The path to the API key file downloaded from the data commons for API access"
    )

    parsed_args = parser.parse_args()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(parsed_args.log_level)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.basicConfig(level=parsed_args.log_level, handlers=[console_handler])

    logger = logging.getLogger(parser.prog)
    logger.setLevel(parsed_args.log_level)

    try:
        logger.info(f'Creating authorization token with key file {parsed_args.api_key_file} on commons {parsed_args.commons_url}', exc_info=True)
        auth = Gen3Auth(parsed_args.commons_url, refresh_file=parsed_args.api_key_file)
    except Exception:
        logger.critical('Caught an exception while generating access token', exc_info=True)
        exit(status)

    try:
        logger.info(f'Creating submission object for {parsed_args.commons_url}')
        submission = Gen3Submission(parsed_args.commons_url, auth)
    except Exception:
        logger.critical('Caught and exceptoin while initializing submission object', exc_info=True)
        exit(status)

    try:
        status = main(parsed_args, submission)
    except Exception:
        logger.critical('Caught an exception', exc_info=True)

    exit(status)
