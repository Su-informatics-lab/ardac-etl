# The release version of the DCC data
__dcc_data_release__ = '2.0.0'
# The version of this mapping software that converts
# DCC data to ARDaC node format files
__mapping_version__ = '1.0.0'
# Node file extension
__node_file_extension__ = '.tsv'
# Node template file extension
__node_template_file_extension__ = '.tsv'

# Get the current DCC data model release and current ARDaC mapping
# implementation versions.
dcc_release_string = f'DCC_data_release_v{__dcc_data_release__}'
mapping_version_string = f'mapping_v{__mapping_version__}'
# Set the case node template file name and the output file names
case_template_file_name = 'submission_case_template' + __node_template_file_extension__
case_obs_file_name = 'case_obs_' + dcc_release_string + __node_file_extension__
case_rct_file_name = 'case_rct_' + dcc_release_string + __node_file_extension__
# Set the audit node template file name and the output file names
audit_template_file_name = 'submission_audit_template' + __node_template_file_extension__
audit_obs_file_name = 'audit_obs_' + dcc_release_string + __node_file_extension__
audit_rct_file_name = 'audit_rct_' + dcc_release_string + __node_file_extension__
audit_obs_unmatched_file_name = 'audit_qc_obs_' + dcc_release_string + __node_file_extension__
audit_rct_unmatched_file_name = 'audit_qc_rct_' + dcc_release_string + __node_file_extension__
# Set the demographic output file names
demographic_template_file_name = 'submission_demographic_template' + __node_template_file_extension__
demographic_obs_file_name = 'demographic_obs_' + dcc_release_string + __node_file_extension__
demographic_rct_file_name = 'demographic_rct_' + dcc_release_string + __node_file_extension__
# Set the follow-up output file names
follow_up_template_file_name = 'submission_follow_up_template' + __node_template_file_extension__
follow_up_obs_file_name = 'follow-up_obs_' + dcc_release_string + __node_file_extension__
follow_up_qc_obs_file_name = 'follow-up_qc_obs_' + dcc_release_string + __node_file_extension__
follow_up_rct_file_name = 'follow-up_rct_' + dcc_release_string + __node_file_extension__
follow_up_qc_rct_file_name = 'follow-up_qc_rct_' + dcc_release_string + __node_file_extension__

