#!/usr/bin/env bash

this_script_name=`basename $0`
MAPPERS_HOME="$(cd "`dirname "$0"`"/..; pwd)"
echo "INFO($this_script_name): MAPPERS_HOME=${MAPPERS_HOME}"

source ${MAPPERS_HOME}/test/test_config.bash

DCC_OBS_SUBJECTS_FILE=${DCC_OBS_PATH}/OBS_SUBJECTS.csv
DCC_RCT_SUBJECTS_FILE=${DCC_RCT_PATH}/RCT_SUBJECTS.csv

DCC_OBS_LIVER_SCORES_FILE=${DCC_OBS_PATH}/OBS_LIVERSCORES.csv
DCC_RCT_LIVER_SCORES_FILE=${DCC_RCT_PATH}/RCT_LIVERSCORES.csv

DCC_OBS_MED_INFO_FILE=${DCC_OBS_PATH}/OBS_MEDINFO.csv

DCC_OBS_VITALS_FILE=${DCC_OBS_PATH}/OBS_VITALS.csv
DCC_RCT_VITALS_FILE=${DCC_RCT_PATH}/RCT_VITALS.csv

DCC_OBS_SOC_FILE=${DCC_OBS_PATH}/OBS_SOC.csv
DCC_RCT_SOC_FILE=${DCC_RCT_PATH}/RCT_SOC.csv

mapper_script=${MAPPERS_HOME}/python/ardac/follow_up_node_mapper.py
echo "INFO($this_script_name): mapper_script=${mapper_script}"

version=$(python ${mapper_script} --version)
echo "INFO($this_script_name): version='${version}'"

dcc_version=$(python ${mapper_script} --dcc_version)
echo "INFO($this_script_name): dcc_version='${dcc_version}'"

mapping_version=$(python ${mapper_script} --mapping_version)
echo "INFO($this_script_name): mapping_version='${mapping_version}'"

python ${mapper_script} --log_level DEBUG --node_templates_path ${NODE_TEMPLATES_PATH} --subjects_type observational --dcc_liver_scores_file ${DCC_OBS_LIVER_SCORES_FILE} --dcc_med_info_file ${DCC_OBS_MED_INFO_FILE} --dcc_vitals_file ${DCC_OBS_VITALS_FILE} --dcc_soc_file ${DCC_OBS_SOC_FILE} --node_output_path ${NODE_OUTPUT_PATH}

python ${mapper_script} --log_level DEBUG --node_templates_path ${NODE_TEMPLATES_PATH} --subjects_type clinical --dcc_liver_scores_file ${DCC_RCT_LIVER_SCORES_FILE} --dcc_med_info_file ${DCC_OBS_MED_INFO_FILE} --dcc_vitals_file ${DCC_RCT_VITALS_FILE} --dcc_soc_file ${DCC_RCT_SOC_FILE} --node_output_path ${NODE_OUTPUT_PATH}

