#!/usr/bin/env bash

MAPPERS_HOME="$(cd "`dirname "$0"`"/..; pwd)"

source ${MAPPERS_HOME}/test/test_config.bash

version=$(${MAPPERS_HOME}/python/ardac --version)
echo "version='${version}'"

dcc_version=$(${MAPPERS_HOME}/python/ardac --dcc_version)
echo "dcc_version='${dcc_version}'"

mapping_version=$(${MAPPERS_HOME}/python/ardac --mapping_version)
echo "mapping_version='${mapping_version}'"


