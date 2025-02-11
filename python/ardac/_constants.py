# The release version of the DCC data
__dcc_data_release__ = '2.0.0'
# The version of this mapping software that converts
# DCC data to ARDaC node format files
__mapping_version__ = '1.0.0'

# Get the current DCC data model release and current ARDaC mapping
# implementation versions.
dcc_release_string = f'DCC_data_release_v{__dcc_data_release__}'
mapping_version_string = f'mapping_v{__mapping_version__}'
# Set the case node template file name and the output file names
case_template_file_name = 'submission_case_template.tsv'
case_obs_file_name = 'case_obs_' + dcc_release_string + '.tsv'
case_rct_file_name = 'case_rct_' + dcc_release_string + '.tsv'
# Set the audit node template file name and the output file names
audit_template_file_name = 'submission_audit_template.tsv'
audit_obs_file_name = 'audit_obs_' + dcc_release_string + '.tsv'
audit_rct_file_name = 'audit_rct_' + dcc_release_string + '.tsv'
audit_obs_unmatched_file_name = 'audit_qc_obs_' + dcc_release_string + '.tsv'
audit_rct_unmatched_file_name = 'audit_qct_rct_' + dcc_release_string + '.tsv'
# Set the demographic output file names
demographic_template_file_name = 'submission_demographic_template.tsv'
