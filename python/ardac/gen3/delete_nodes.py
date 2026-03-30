import argparse
import logging
import sys
from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

def main(commons_url: str, program_name: str, project_name: str, node_type: str, api_key_file: str):
    # Set up the URL of the Gen3 commons you're working with

    # program_name = "ARDaC"
    # commons_url = 'https://your-gen3-commons.org/'

    # program_name = "DEMO"
    # commons_url = 'https://your-demo-commons.org/'

    # program_name = "ORIEN"
    # commons_url = 'https://your-orien-commons.org/'

    # Authenticate using your credentials file (JSON format)
    # credentials = f"./credentials_{program_name}.json"
    auth = Gen3Auth(commons_url, refresh_file=api_key_file)

    # Instantiate the Gen3Submission class to interact with the submission API
    submission = Gen3Submission(commons_url, auth)

    # Specify the program, project, and the type of node to be deleted

    # program = "ARDaC"
    # project = "AlcHepNet"
    # node_type = "lab"

    # program = "ARDaC"
    # project = "AlcHepNet"
    # node_type = "aliquot"

    # program = "ORIEN"
    # project = "Avatar"
    # node_type = "aliquot"

    # Delete the node of the specified type from the program and project
    logger.info(f"Attempting to delete node...")
    logger.info(f"Program: {program_name}")
    logger.info(f"Project: {project_name}")
    logger.info(f"Node Type: {node_type}")
    response = submission.delete_node(program_name, project_name, node_type)
    logger.info(f"Response received: {response}")

    if response is None:
        logger.critical(f"No response returned. Please check your website.")
    elif response.status_code == 200:
        logger.info(f"Successfully deleted node '{node_type}' from program '{program_name}' and project '{project_name}'.")
    else:
        logger.error(f"Failed to delete node: {response.status_code} - {response.text}")


if __name__ == "__main__":
    status = 3
    parser = argparse.ArgumentParser(
        description="""This utility deletes all records from a Gen3 metadata repository for a specified node type."""
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
        "--project-name",
        dest="project_name",
        required=True,
        help="The project name from which the node data will be deleted"
    )
    parser.add_argument(
        "--node-type",
        dest="node_type",
        required=True,
        help="The type of the node to delete"
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
        status = main(parsed_args.commons_url, parsed_args.program_name, parsed_args.project_name, parsed_args.node_type, parsed_args.api_key_file)
    except FileNotFoundError as e:
        logger.critical("Credentials file not found: %s", e.filename)
    except Exception as e:
        logger.critical("Caught an exception", exc_info=True)

    exit(status)



    


