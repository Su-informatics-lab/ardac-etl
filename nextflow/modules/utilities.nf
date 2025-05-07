// This function maps the subjects type to the
// ARDaC observational or clinical case node file
// name. 
def mapSubjectsTypeToCaseNodeFile(subjects_type) {
   if (subjects_type == "observational") {
      return "case_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "case_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}

// This function maps the subjects type to the
// ARDaC observational or clinical demographic node file
// name. 
def mapSubjectsTypeToDemographicNodeFile(subjects_type) {
   if (subjects_type == "observational") {
      return "demographic_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "demographic_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}

// This function maps the subjects type to the
// ARDaC observational or clinical follow-up node file name
def mapSubjectsTypeToFollowupNodeFile(subjects_type) {
   if (subjects_type == "observational") {
      return "follow-up_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "follow-up_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}

// This function maps the subjects type to the
// ARDaC observational or clinical follow-up quality
// control file name
def mapSubjectsTypeToFollowupQCFile(subjects_type) {
   if (subjects_type == "observational") {
      return "follow-up_qc_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "follow-up_qc_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}

// This function maps the subjects type to the
// ARDaC observational or clinical audit node file name
def mapSubjectsTypeToAuditNodeFile(subjects_type) {
   if (subjects_type == "observational") {
      return "audit_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "audit_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}

// This function maps the subjects type to the
// ARDaC observational or clinical audit quality
// control file name
def mapSubjectsTypeToAuditQCFile(subjects_type) {
   if (subjects_type == "observational") {
      return "audit_qc_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "audit_qc_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}