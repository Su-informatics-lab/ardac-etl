#!/usr/bin/env nextflow

include { mapSubjectsTypeToCaseFile } from './utilities.nf'

/*
 * Generate a case node from observational or clinical trial DCC subect data
 * provided in CSV format files.
 */
process CASE_NODE_MAPPER {

    //publishDir params.output, mode: 'symlink'

    input:
        // Path to directory containing node template files
        path node_templates_path
        // Path to the DCC subject file
        path dcc_subjects_file 
        // Path to the output directory
        path node_output_path
        // The subjects type
        val subjects_type

    output:
        path("${node_output_path}/" + mapSubjectsTypeToCaseFile(subjects_type))
        
    script:
    """
    python case_node_maper.py \
       --log_level ${params.python_log_level} \
       --node_templates_path ${node_templates_path} \
       --subjects-type ${subjects_type} \
       --dcc_subjects_file ${dcc_subjects_file} \
       --node_output_path ${node_output_path}
    """
}