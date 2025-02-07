import os
import sys
import errno
import argparse
import logging
import version
import pandas as pd
from pathlib import Path

# Get the current DCC data model release and current ARDaC mapping
# implementation versions.
dcc_release_string = f'DCC_data_release_v{version.__dcc_data_release__}'
mapping_version_string = f'mapping_v{version.__mapping_version__}'
# Set the case node template file name and the output file names
case_template_file_name = 'submission_case_template.tsv'
case_obs_file = 'case_obs_' + dcc_release_string + '.tsv'
case_rct_file = 'case_rct_' + dcc_release_string + '.tsv'


def generate_observational_case_node(obs_file_path: Path, template_headers: list[str]) -> pd.DataFrame:
   """
   This function takes the path to observational subject data and generates
   a pandas dataframe containing the ARDaC case node data for the observational
   subjects.

   Parameters
   ----------
   obs_file_path : Path
      The full path to the observational subject data CSV file from which data
      will be extracted to populate the ARDaC case node.
   template_headers : list[str]
      The headers extracted from the case node template

   Return
   ------
   A pandas dataframe containing the ARDaC case node data derived from the
   observational subjects
   """
   # Read the file using pandas
   logger.info(f'Reading subjects file: {obs_file_path.as_posix()}')
   df_obs_input = pd.read_csv(obs_file_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading subjects file')

   # Initialize a DataFrame with the defined headers and same index as df_obs_input
   df_obs_output = pd.DataFrame(index=df_obs_input.index, columns=template_headers)

   # Initialize a DataFrame with the defined headers and same index as df_obs_input
   df_obs_output = pd.DataFrame(index=df_obs_input.index, columns=template_headers)

   # Assign fixed values using .loc to align with the index
   df_obs_output.loc[:, "*type"] = "case"
   df_obs_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
   df_obs_output.loc[:, "*studies.submitter_id"] = "obs"
   df_obs_output.loc[:, "index_date"] = "Study Enrollment"

   # Map dynamic values using .apply
   df_obs_output["*submitter_id"] = df_obs_input["usubjid"].apply(lambda x: f"{x}_obs" if pd.notna(x) else None)
   df_obs_output["cohort"] = df_obs_input["obs_arm"].apply(lambda x: x.split(":")[-1].strip() if pd.notna(x) else None)
   df_obs_output["study_site"] = df_obs_input["site"].apply(lambda x: x.strip() if pd.notna(x) else None)
   df_obs_output["vital_status"] = df_obs_input["ALIVE"].apply(lambda x: "alive" if x == "Y" else "dead" if x == "N" else None)

   return df_obs_output


def generate_clinical_case_node(rct_file_path: Path, template_headers: list[str]) -> pd.DataFrame:
   """
   This function takes the path to clinical subject data and generates
   a pandas dataframe containing the ARDaC case node data for the clinical
   subjects.

   Parameters
   ----------
   rct_file_path : Path
      The full path to the clinical subject data CSV file from which data
      will be extracted to populate the ARDaC case node.
   template_headers : list[str]
      The headers extracted from the case node template

   Return
   ------
   A pandas dataframe containing the ARDaC case node data derived from the
   clinical subjects
   """
   # Read the RCT_SUBJECTS.csv file
   logger.info(f'Reading subjects file: {rct_file_path.as_posix()}')
   df_rct_input = pd.read_csv(rct_file_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading subjects file')

   # Initialize a new DataFrame with the defined headers and the same index as df_input_rct
   df_rct_output = pd.DataFrame(index=df_rct_input.index, columns=template_headers)

   # Assign fixed values using .loc for proper alignment
   df_rct_output.loc[:, "*type"] = "case"
   df_rct_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
   df_rct_output.loc[:, "*studies.submitter_id"] = "clinical"
   df_rct_output.loc[:, "index_date"] = "Study Enrollment"

   # Map dynamic values based on the input file
   df_rct_output["*submitter_id"] = df_rct_input["usubjid"].apply(lambda x: f"{x}_clinical" if pd.notna(x) else None)
   df_rct_output["actarm"] = df_rct_input["rct_arm"].apply(lambda x: x.strip() if pd.notna(x) else None)
   df_rct_output["rct_meld_strata"] = df_rct_input["rct_meld_strata"].apply(lambda x: x.strip() if pd.notna(x) else None)
   df_rct_output["study_site"] = df_rct_input["site"].apply(lambda x: x.strip() if pd.notna(x) else None)
   df_rct_output["vital_status"] = df_rct_input["ALIVE"].apply(lambda x: "alive" if x == "Y" else "dead" if x == "N" else None)

   # Fill other unmapped columns with NaN for consistency
   for col in df_rct_output.columns:
      if col not in ["*type", "project_id", "*submitter_id", "*studies.submitter_id", "actarm", 
                     "rct_meld_strata", "study_site", "vital_status", "index_date"]:
         df_rct_output[col] = None

   return df_rct_output



def main(command_arguments: argparse.Namespace, logger: logging.Logger) -> int:
   """
   This function implements the steps needed for converting observational or clinical
   subject data into an ARDaC case node.  The subject data is provided in a CSV file
   and converted to an ARDaC case node file in TSV format containing the fields given in
   the ARDaC case template.

   Parameters
   ----------
   command_arguments : argparse.Namespace
      The command line arguments processed by argparse
   logger : logging.Logger
      The logger to be used to provide user feedback
   """
   template_path = Path(command_arguments.nodeTemplatesPath, case_template_file_name)
   subjects_path = Path(command_arguments.subjectsFile)
   node_output_path = Path(command_arguments.nodeOutputPath)

   if not template_path.is_file():
      logger.critical('Cannot find case template file: ' + template_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path.as_posix())
   
   if not subjects_path.is_file():
      logger.critical('Cannot find subjects file: ' + subjects_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), subjects_path.as_posix())
   
   if not node_output_path.is_dir():
      logger.critical('Cannot find node output directory: ' + node_output_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), node_output_path.as_posix())
   
   # Read the template TSV file to extract the headers
   logger.info(f'Reading case template CSV file: {template_path.as_posix()}')
   df_template = pd.read_csv(template_path.as_posix(), sep="\t", nrows=0)  # Read only the header
   template_headers = df_template.columns.tolist()  # Extract the headers as a list

   if command_arguments.subjects_type == 'observational':
      logger.info('Transforming observational data')
      node_file_path = Path(node_output_path, case_obs_file)
      df_obs_output = generate_observational_case_node(subjects_path, template_headers)
      df_obs_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
   elif command_arguments.subjects_type == 'clinical':
      logger.info('Transforming clinical data')
      node_file_path = Path(node_output_path, case_rct_file)
      df_rct_output = generate_clinical_case_node(subjects_path, template_headers)
      df_rct_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, headers=True)
   else:
      raise ValueError(f'Processing for subjects_type={command_arguments.subjects_type} is not implemented')

   
if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      description='''This utility generates ARDaC case nodes from observational or clinical trial subjects provided in CSV format files.
         The user must provide the location of the ARDaC node template files, the CSV file containing the case data to ARDaC format, and the path to where the ARDaC case node file is to be written.''',
      epilog=f'''Clinical trial case node files are named \'case_rct_{dcc_release_string}.tsv\'.
         Observational case node files are named \'case_obs_{dcc_release_string}.tsv\'''')
   valid_log_level_names_mapping = logging.getLevelNamesMapping()
   valid_log_level_names_mapping.pop('NOTSET') # Remove NOTSET option value
   parser.add_argument('--version', action='version', version=f'{dcc_release_string}_{mapping_version_string}')
   parser.add_argument('--log_level', dest='logLevel', default='INFO', choices=list(valid_log_level_names_mapping.keys()), help='A standard log level from the Python logger package')
   parser.add_argument('--node_templates_path', dest='nodeTemplatesPath', required=True, help='Path to the directory where the ARDaC node template TSV files are located')
   parser.add_argument('--subjects_type', dest='subjectsType', required=True, choices=['observational', 'clinical'], help='Value indicating if the input subject data is from clinical trial subjects or observational study subjects')
   parser.add_argument('--subjects_file', dest='subjectsFile', required=True, help='Full path to the CSV input subjects file')
   parser.add_argument('--node_output_path', dest='nodeOutputPath', required=True, help='Path to the directory where the TSV case node file is to be saved.  Do not include a file name at the end, it will be autogenerated.')

   parsed_args = parser.parse_args()
   print(parsed_args)
   
   # Configure and create logger for standard error
   console_handler = logging.StreamHandler(sys.stderr)
   console_handler.setLevel(parsed_args.logLevel)
   console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

   logging.basicConfig(
      level = parsed_args.logLevel,
      handlers = [console_handler]
   )

   logger = logging.getLogger(parser.prog)
   logger.setLevel(parsed_args.logLevel)

   try:
      # Status codes greater than zero and less than three are reserved for command line processing errors
      status = 3
      status = main(parsed_args, logger)
   except FileNotFoundError as e:
      logger.critical(f'Input file not found: {e}')
   except Exception as e:
      logger.critical('Caught an exception', exc_info=True)
   
   exit(status)