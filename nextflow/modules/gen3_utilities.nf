#!/usr/bin/env nextflow

/*
 * Delete all records of a specified node type from a Gen3 data commons.
 * This process runs as an initialization step and does not produce outputs
 * that downstream processes depend on.
 */
process DELETE_NODES {
   input:
      // The URL of the Gen3 data commons to access
      val commons_url
      // The program name in the Gen3 data commons
      val program_name
      // The project name in the Gen3 data commons
      val project_name
      // The type of node to delete
      val node_type
      // The path to the API key file for authentication
      path api_key_file

   script:
   """
   python ${params.gen3_utilities_scripts}/delete_nodes.py \
       --log_level ${params.python_log_level} \
       --commons-url ${commons_url} \
       --program-name ${program_name} \
       --project-name ${project_name} \
       --node-type ${node_type} \
       --api-key-file ${api_key_file}
   """
}
