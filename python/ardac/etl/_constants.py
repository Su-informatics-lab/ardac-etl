# The release version of the DCC data
__dcc_data_release__ = '2.0.0'
# The version of this mapping software that converts
# DCC data to ARDaC node format files
__mapping_version__ = '1.0.1'
# Node file extension
__node_file_extension__ = '.tsv'
# Node template file extension
__node_template_file_extension__ = '.tsv'

# Get the current DCC data model release and current ARDaC mapping
# implementation versions.
DCC_RELEASE_STRING = f'DCC_data_release_v{__dcc_data_release__}'
MAPPING_VERSION_STRING = f'mapping_v{__mapping_version__}'
# Set the case node template file name and the output file names
CASE_TEMPLATE_FILE_NAME = 'submission_case_template' + __node_template_file_extension__
CASE_OBS_FILE_NAME = 'case_obs_' + DCC_RELEASE_STRING + __node_file_extension__
CASE_RCT_FILE_NAME = 'case_rct_' + DCC_RELEASE_STRING + __node_file_extension__
# Set the audit node template file name and the output file names
AUDIT_TEMPLATE_FILE_NAME = 'submission_audit_template' + __node_template_file_extension__
AUDIT_OBS_FILE_NAME = 'audit_obs_' + DCC_RELEASE_STRING + __node_file_extension__
AUDIT_RCT_FILE_NAME = 'audit_rct_' + DCC_RELEASE_STRING + __node_file_extension__
AUDIT_OBS_UNMATCHED_FILE_NAME = 'audit_qc_obs_' + DCC_RELEASE_STRING + __node_file_extension__
AUDIT_RCT_UNMATCHED_FILE_NAME = 'audit_qc_rct_' + DCC_RELEASE_STRING + __node_file_extension__
# Set the demographic output file names
DEMOGRAPHIC_TEMPLATE_FILE_NAME = 'submission_demographic_template' + __node_template_file_extension__
DEMOGRAPHIC_OBS_FILE_NAME = 'demographic_obs_' + DCC_RELEASE_STRING + __node_file_extension__
DEMOGRAPHIC_RCT_FILE_NAME = 'demographic_rct_' + DCC_RELEASE_STRING + __node_file_extension__
# Set the follow-up output file names
FOLLOW_UP_TEMPLATE_FILE_NAME = 'submission_follow_up_template' + __node_template_file_extension__
FOLLOW_UP_OBS_FILE_NAME = 'follow-up_obs_' + DCC_RELEASE_STRING + __node_file_extension__
FOLLOW_UP_QC_OBS_FILE_NAME = 'follow-up_qc_obs_' + DCC_RELEASE_STRING + __node_file_extension__
FOLLOW_UP_RCT_FILE_NAME = 'follow-up_rct_' + DCC_RELEASE_STRING + __node_file_extension__
FOLLOW_UP_QC_RCT_FILE_NAME = 'follow-up_qc_rct_' + DCC_RELEASE_STRING + __node_file_extension__
