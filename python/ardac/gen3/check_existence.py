import argparse
from argparse import Namespace
import json
import logging
import sys
from gen3.submission import Gen3Submission
from gen3.auth import Gen3Auth
from gen3.query import Gen3Query

def main(parsed_args: Namespace, query: Gen3Submission) -> int:
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f'Checking if record exists: program={parsed_args.program_name}, '
                   f'project={parsed_args.project_name}, node_type={parsed_args.node_type}, '
                   f'submitter_id={parsed_args.submitter_id}')
        
        # Query the Gen3 commons to check if the record exists
        #query_string = f"""
        #query {{
        #    {parsed_args.node_type}(filter: {{submitter_id: {{eq: "{parsed_args.submitter_id}"}}}}, 
        #                first: 1) {{
        #        id
        #        submitter_id
        #    }}
        #}}
        #"""
        
        # This is for the flat query, but that service is not active in ARDaC
        #result = query.query(
        #    data_type=f"{parsed_args.node_type}",
        #    first=1,
        #    fields=[
        #        "submitter_id"
        #    ],
        #    filters={"submitter_id": f"{parsed_args.submitter_id}"},
        #    sort_object={"submitter_id": "asc"}
        #)

        query_str = f"""{{
            {parsed_args.node_type}(submitter_id: \"{parsed_args.submitter_id}\") {{
                submitter_id
                id
            }}
        }}"""

        result = query.query(query_str)

        logger.debug(f'Query result: {result}')
        
        # Check if any records were found
        if result and 'data' in result:
            data = result['data']
            if data and parsed_args.node_type in data and len(data[parsed_args.node_type]) > 0:
                logger.info(f'Record with submitter_id "{parsed_args.submitter_id}" exists')
                return 0
        
        logger.info(f'Record with submitter_id "{parsed_args.submitter_id}" does not exist')
        return 1
        
    except FileNotFoundError:
        logger.error(f'JSON file not found: {parsed_args.json_file}', exc_info=True)
        return 2
    except json.JSONDecodeError as e:
        logger.error(f'Failed to parse JSON file: {e}', exc_info=True)
        return 2
    except Exception as e:
        logger.error(f'Error checking if record exists: {e}', exc_info=True)
        return 2
    

if __name__ == "__main__":
    status = 3
    parser = argparse.ArgumentParser(
        description="""This utility checks if a record, given a node type and submitter_id value, exists.""",
        epilog="""If the record does exist, a status code of 0 is returned.  If the record does not exist, a status code of 1 is returned.
           If some kind of error occurred, a status code of 2 or greater is returned."""
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
        help="The program name under which the record will be searched for"
    )
    parser.add_argument(
        "--project-name",
        dest="project_name",
        required=True,
        help="The project name under which the record will be searched for"
    )
    parser.add_argument(
        "--node-type",
        dest="node_type",
        required=True,
        help="The node type of the target record"
    )
    parser.add_argument(
        "--submitter-id",
        dest="submitter_id",
        required=True,
        help="The ID of the record to extract"
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
        logger.critical('Caught an exception while generating the access token', exc_info=True)
        exit(status)

    try:
        logger.info(f'Creating query object for {parsed_args.commons_url}')
        query = Gen3Submission(auth)
    except Exception:
        logger.critical('Caught an exception while initializing the query object', exc_info=True)
        exit(status)

    try:
        status = main(parsed_args, query)
    except Exception:
        logger.critical('Caught an exception', exc_info=True)

    exit(status)
