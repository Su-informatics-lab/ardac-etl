import argparse
from argparse import Namespace
import json
import logging
import sys
from gen3.submission import Gen3Submission
from gen3.auth import Gen3Auth
from gen3.query import Gen3Query

def main(parsed_args: Namespace, submission: Gen3Submission) -> int:
    try:
        jsonSchema = submission.get_graphql_schema()

        with open(parsed_args.schema_file, 'w') as f:
            json.dump(jsonSchema, f, indent=4)
        
    except FileNotFoundError:
        logger.error(f'JSON file not found: {parsed_args.json_file}', exc_info=True)
        return 2
    except json.JSONDecodeError as e:
        logger.error(f'Failed to parse JSON file: {e}', exc_info=True)
        return 2
    except Exception as e:
        logger.error(f'Error checking if record exists: {e}', exc_info=True)
        return 2
    
    return 0
    

if __name__ == "__main__":
    status = 3
    parser = argparse.ArgumentParser(
        description="""This dumps the GraphQL schema for a given Gen3 instance and saves it to a file"""
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
        "--schema-file",
        dest="schema_file",
        required=True,
        help="The path to the file the schema will be written to"
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
        logger.info(f'Creating authorization token with key file {parsed_args.api_key_file} on commons {parsed_args.commons_url}')
        auth = Gen3Auth(parsed_args.commons_url, refresh_file=parsed_args.api_key_file)
    except Exception:
        logger.critical('Caught an exception while generating the access token', exc_info=True)
        exit(status)

    try:
        logger.info(f'Creating query object for {parsed_args.commons_url}')
        submission = Gen3Submission(auth)
    except Exception:
        logger.critical('Caught an exception while initializing the query object', exc_info=True)
        exit(status)

    try:
        status = main(parsed_args, submission)
    except Exception:
        logger.critical('Caught an exception', exc_info=True)

    exit(status)
