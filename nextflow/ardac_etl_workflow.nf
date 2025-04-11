#!/usr/bin/env nextflow

include { CASE_NODE_MAPPER } from './modules/mappers.nf'
include { GET_MAPPER_DCC_VERSION } from './modules/mappers.nf'
include { DEMOGRAPHIC_NODE_MAPPER } from './modules/mappers.nf'
include { FOLLOWUP_NODE_MAPPER } from './modules/mappers.nf'

workflow {

   // params.subjects_type should be provided on the command line
   subjects_type = params.subjects_type
   input_dir = file(params.input_directory)
   node_templates_path = input_dir.resolve(params.node_templates_directory)
   dcc_obs_subjects_file = input_dir.resolve(params.observational_subjects_csv_file)
   dcc_rct_subjects_file = input_dir.resolve(params.clinical_subjects_csv_file)
   dcc_obs_liver_scores_file = input_dir.resolve(params.observational_liver_scores_csv_file)
   dcc_rct_liver_scores_file = input_dir.resolve(params.clinical_liver_scores_csv_file)
   dcc_obs_med_info_file = input_dir.resolve(params.observational_med_info_csv_file)
   dcc_rct_med_info_file = input_dir.resolve(params.clinical_med_info_csv_file)
   dcc_obs_vitals_file = input_dir.resolve(params.observational_vitals_csv_file)
   dcc_rct_vitals_file = input_dir.resolve(params.clinical_vitals_csv_file)
   dcc_obs_soc_file = input_dir.resolve(params.observational_soc_csv_file)
   dcc_rct_soc_file = input_dir.resolve(params.clinical_soc_csv_file)
   node_output_path = input_dir.resolve(params.ardac_nodes_directory)

   if (subjects_type == 'observational') {
      dcc_subjects_file = dcc_obs_subjects_file
      dcc_liver_scores_file = dcc_obs_liver_scores_file
      dcc_med_info_file = dcc_obs_med_info_file
      dcc_vitals_file = dcc_obs_vitals_file
      dcc_soc_file = dcc_obs_soc_file
   } else if (subjects_type == 'clinical') {
      dcc_subjects_file = dcc_rct_subjects_file
      dcc_liver_scores_file = dcc_rct_liver_scores_file
      dcc_med_info_file = dcc_rct_med_info_file
      dcc_vitals_file = dcc_rct_vitals_file
      dcc_soc_file = dcc_rct_soc_file
   } else {
      log.info "Unsupported subject type given: ${subjects_type}"
      error "Unsupported subjects type: ${subjects_type}"
   }

   log.info "---------------------"
   log.info "Workflow parameters: "
   log.info "---------------------"
   log.info "subjects_type        : ${subjects_type}"
   log.info "input_dir            : ${input_dir}"
   log.info "node_templates_path  : ${node_templates_path}"
   log.info "dcc_obs_subjects_file: ${dcc_obs_subjects_file}"
   log.info "dcc_rct_subjects_file: ${dcc_rct_subjects_file}"
   log.info "node_output_path     : ${node_output_path}"

   GET_MAPPER_DCC_VERSION()
   mapper_dcc_version = GET_MAPPER_DCC_VERSION.out.mapper_dcc_version

   mapper_dcc_version.view { path ->
      if (path.text != params.release)
         error "Mapper DCC version (${path.text}) does not match NextFlow DCC version (${params.release})"
   }

   CASE_NODE_MAPPER(node_templates_path, dcc_subjects_file, node_output_path, subjects_type)

   DEMOGRAPHIC_NODE_MAPPER(node_templates_path, dcc_subjects_file, node_output_path, subjects_type, CASE_NODE_MAPPER.case_node_file)
   
   FOLLOWUP_NODE_MAPPER(node_templates_path, dcc_subjects_file, dcc_liver_scores_file, dcc_med_info_file, dcc_vitals_file, dcc_soc_file, node_output_path, subjects_type, CASE_NODE_MAPPER.case_node_file)
}