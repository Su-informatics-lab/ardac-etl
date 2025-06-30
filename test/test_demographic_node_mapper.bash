#!/usr/bin/env bash

this_script_name=`basename $0`
MAPPERS_HOME="$(cd "`dirname "$0"`"/..; pwd)"
echo "INFO($this_script_name): MAPPERS_HOME=${MAPPERS_HOME}"

source ${MAPPERS_HOME}/test/test_config.bash

DCC_OBS_SUBJECTS_FILE=${DCC_OBS_PATH}/OBS_SUBJECTS.csv
DCC_RCT_SUBJECTS_FILE=${DCC_RCT_PATH}/RCT_SUBJECTS.csv

mapper_script=${MAPPERS_HOME}/python/ardac/demographic_node_mapper.py
echo "INFO($this_script_name): mapper_script=${mapper_script}"

version=$(python ${mapper_script} --version)
echo "INFO($this_script_name): version='${version}'"

dcc_version=$(python ${mapper_script} --dcc_version)
echo "INFO($this_script_name): dcc_version='${dcc_version}'"

mapping_version=$(python ${mapper_script} --mapping_version)
echo "INFO($this_script_name): mapping_version='${mapping_version}'"

python ${mapper_script} --log_level DEBUG --node_templates_path ${NODE_TEMPLATES_PATH} --subjects_type observational --dcc_subjects_file ${DCC_OBS_SUBJECTS_FILE} --node_output_path ${NODE_OUTPUT_PATH}

python ${mapper_script} --log_level DEBUG --node_templates_path ${NODE_TEMPLATES_PATH} --subjects_type clinical --dcc_subjects_file ${DCC_RCT_SUBJECTS_FILE} --node_output_path ${NODE_OUTPUT_PATH}
