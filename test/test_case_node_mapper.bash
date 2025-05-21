#!/usr/bin/env bash

this_script_name=`basename $0`
MAPPERS_HOME="$(cd "`dirname "$0"`"/..; pwd)"

source ${MAPPERS_HOME}/test/test_config.bash

conda activate ${MAPPERS_HOME}/venv
conda_activation_status=$?

if [[ $conda_activation_status -ne 0 ]]
then
   echo "ERROR($this_script_name): Failed to activate Python virtual environment" 1>&2
   exit ${VIRTUAL_ENVIRONMENT_FAILURE}
fi


mapper_script=${MAPPERS_HOME}/python/ardac/case_node_mapper.py

version=$(python ${mapper_script} --version)
echo "INFO($this_script_name): version='${version}'"

dcc_version=$(python ${mapper_script} --dcc_version)
echo "INFO($this_script_name): dcc_version='${dcc_version}'"

mapping_version=$(python ${mapper_script} --mapping_version)
echo "INFO($this_script_name): mapping_version='${mapping_version}'"


