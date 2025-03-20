// This function maps the subjects type to the
// ARDaC observational or clinical case node file
// name. 
def mapSubjectsTypeToCaseFile(subjects_type) {
   if (subjects_type == "observational") {
      return "case_obs_" + params.dcc_release + ".tsv"
   } else if (subjects_type == "clinical") {
      return "case_rct_" + params.dcc_release + ".tsv"
   }

   error "Unsupported subjects_type value: " + subjects_type
}