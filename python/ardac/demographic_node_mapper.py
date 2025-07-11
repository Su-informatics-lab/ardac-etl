import os
import sys
import errno
import argparse
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import _constants


def generate_observational_demographic_node(obs_subjects_path: Path, obs_case_path: Path, template_headers: list[str]) -> pd.DataFrame:
   """
   This function takes the path to the DCC observational subjects file, the ARDaC observational case node file,
   and the ARDaC demographic node headers and produces the ARDaC demographic node data.

   Parameters
   ----------
   obs_subjects_path : Path
      The full path to the subjects file for the DCC observational data
   obs_case_path : Path
      The full path to the ARDaC case node file generated by case_node_mapper.py
   template_headers : list[str]
      The header names extracted from the demographic node template

   Return
   ------
   A pandas dataframe containing the ARDaC demographic node data derived from the
   observational subjects
   """
   # Read the file using pandas
   logger.info(f'Reading the observational subjects file: {obs_subjects_path.as_posix()}')
   df_obs_subjects_input = pd.read_csv(obs_subjects_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational subjects file')

   logger.info(f'Reading the observational ARDaC case file: {obs_case_path.as_posix()}')
   df_obs_case_input = pd.read_csv(obs_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading observational case file')

   df_obs_output = pd.DataFrame(index=df_obs_subjects_input.index, columns=template_headers)

   # Step 1: Extract "*submitter_id" from df_obs_case and create case_table
   case_table = pd.DataFrame()
   case_table["*submitter_id"] = df_obs_case_input["*submitter_id"]
   case_table["usubjid"] = case_table["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"

   # Step 2: Iterate through case_table and map values to df_obs_output
   for _, row in case_table.iterrows():
      submitter_id = row["*submitter_id"]
      usubjid = row["usubjid"]

      # Find the corresponding record in df_obs_input
      input_row = df_obs_subjects_input[df_obs_subjects_input["usubjid"] == usubjid]

      if not input_row.empty:
         input_row = input_row.iloc[0]  # Extract the first matching row

         # Populate df_obs_output
         df_obs_output.loc[:, "*type"] = "demographic"
         df_obs_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
         df_obs_output.loc[_, "*submitter_id"] = f"{submitter_id}_demographic"
         df_obs_output.loc[_, "*cases.submitter_id"] = f"{submitter_id}"
         df_obs_output.loc[_, "age_at_index"] = input_row.get("calc_age", None)
         df_obs_output.loc[_, "cause_of_death_primary"] = input_row.get("codp", None)
         df_obs_output.loc[_, "cause_of_death_secondary"] = input_row.get("cods", None)
         df_obs_output.loc[_, "cur_employ_stat"] = input_row.get("employed", None)
         df_obs_output.loc[_, "education"] = input_row.get("edu", None)
         df_obs_output.loc[_, "ethnicity"] = input_row.get("ethnic", None)
         df_obs_output.loc[_, "gender"] = input_row.get("gender", None)
         df_obs_output.loc[_, "marital"] = input_row.get("maristat", None)
         df_obs_output.loc[_, "race"] = input_row.get("race", None)
         df_obs_output.loc[_, "sex"] = input_row.get("sex", None)

         # Map "vital_status" from "ALIVE"
         alive = input_row.get("ALIVE", "").strip()
         if alive == "Y":
            df_obs_output.loc[_, "vital_status"] = "Alive"
         elif alive == "N":
            df_obs_output.loc[_, "vital_status"] = "Dead"
         else:
            df_obs_output.loc[_, "vital_status"] = "Not Reported"

         # Extract "year_of_birth" and "year_of_death"
         brthdtc = input_row.get("brthdtc", None)
         df_obs_output.loc[_, "year_of_birth"] = brthdtc.split("-")[0] if pd.notna(brthdtc) else None

         dthdtc = input_row.get("dthdtc", None)
         df_obs_output.loc[_, "year_of_death"] = dthdtc.split("-")[0] if pd.notna(dthdtc) else None

         # Calculate "days_to_death"
         scdat = input_row.get("scdat", None)  # Study enrollment date
         if pd.notna(dthdtc) and pd.notna(scdat):
            try:
               death_date = datetime.strptime(dthdtc, "%Y-%m-%d")
               study_date = datetime.strptime(scdat, "%Y-%m-%d")
               days_to_death = (death_date - study_date).days
               df_obs_output.loc[_, "days_to_death"] = days_to_death
            except ValueError:
                df_obs_output.loc[_, "days_to_death"] = None

   return df_obs_output


def generate_clinical_demographic_node(rct_subjects_path: Path, rct_case_path: Path, template_headers: list[str]) -> pd.DataFrame:
   """
   This function takes the path to the DCC clinical subjects file, the ARDaC clinical case node file,
   and the ARDaC demographic node headers to produce the ARDaC demographic node data.

   Parameters
   ----------
   rct_subjects_path : Path
      The full path to the subjects file for the DCC clinical data
   rct_case_path : Path
      The full path to the ARDaC case node file generated by case_node_mapper.py
   template_headers : list[str]
      The header names extracted from the demographic node template

   Return
   ------
   A pandas dataframe containing the ARDaC demographic node data derived from the
   clinical subjects
   """
   # Read the file using pandas
   logger.info(f'Reading the clinical subjects file: {rct_subjects_path.as_posix()}')
   df_rct_subjects_input = pd.read_csv(rct_subjects_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical subjects file')

   logger.info(f'Reading the clinical ARDaC case file: {rct_case_path.as_posix()}')
   df_rct_case_input = pd.read_csv(rct_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading clinical case file')

   df_rct_output = pd.DataFrame(index=df_rct_subjects_input.index, columns=template_headers)

   # Step 1: Extract "*submitter_id" from df_rct_case and create case_table
   case_table = pd.DataFrame()
   case_table["*submitter_id"] = df_rct_case_input["*submitter_id"]
   case_table["usubjid"] = case_table["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"

   # Step 2: Iterate through case_table and map values to df_rct_output
   for _, row in case_table.iterrows():
      submitter_id = row["*submitter_id"]
      usubjid = row["usubjid"]

      # Find the corresponding record in df_rct_input
      input_row = df_rct_subjects_input[df_rct_subjects_input["usubjid"] == usubjid]

      if not input_row.empty:
         input_row = input_row.iloc[0]  # Extract the first matching row

         # Populate df_rct_output
         df_rct_output.loc[:, "*type"] = "demographic"
         df_rct_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
         df_rct_output.loc[_, "*submitter_id"] = f"{submitter_id}_demographic"
         df_rct_output.loc[_, "*cases.submitter_id"] = f"{submitter_id}"
         df_rct_output.loc[_, "age_at_index"] = input_row.get("calc_age", None)
         df_rct_output.loc[_, "cause_of_death_primary"] = input_row.get("codp", None)
         df_rct_output.loc[_, "cause_of_death_secondary"] = input_row.get("cods", None)
         df_rct_output.loc[_, "cur_employ_stat"] = input_row.get("employed", None)
         df_rct_output.loc[_, "education"] = input_row.get("edu", None)
         df_rct_output.loc[_, "ethnicity"] = input_row.get("ethnic", None)
         df_rct_output.loc[_, "gender"] = input_row.get("gender", None)
         df_rct_output.loc[_, "marital"] = input_row.get("maristat", None)
         df_rct_output.loc[_, "race"] = input_row.get("race", None)
         df_rct_output.loc[_, "sex"] = input_row.get("sex", None)

         # Map "vital_status" from "ALIVE"
         alive = input_row.get("ALIVE", "").strip()
         if alive == "Y":
            df_rct_output.loc[_, "vital_status"] = "Alive"
         elif alive == "N":
            df_rct_output.loc[_, "vital_status"] = "Dead"
         else:
            df_rct_output.loc[_, "vital_status"] = "Not Reported"

         # Extract "year_of_birth" and "year_of_death"
         brthdtc = input_row.get("brthdtc", None)
         df_rct_output.loc[_, "year_of_birth"] = brthdtc.split("-")[0] if pd.notna(brthdtc) else None

         dthdtc = input_row.get("dthdtc", None)
         df_rct_output.loc[_, "year_of_death"] = dthdtc.split("-")[0] if pd.notna(dthdtc) else None

         # Calculate "days_to_death"
         scdat = input_row.get("scdat", None)  # Study enrollment date
         if pd.notna(dthdtc) and pd.notna(scdat):
            try:
               death_date = datetime.strptime(dthdtc, "%Y-%m-%d")
               study_date = datetime.strptime(scdat, "%Y-%m-%d")
               days_to_death = (death_date - study_date).days
               df_rct_output.loc[_, "days_to_death"] = days_to_death
            except ValueError:
                df_rct_output.loc[_, "days_to_death"] = None

   return df_rct_output


def main(command_arguments: argparse.Namespace, logger: logging.Logger) -> int:
   """
   This function implements the steps needed for converting observational or clinical
   subject and case data into an ARDaC  node.  The subject data is provided in a CSV file
   and converted to an ARDaC demographic node file in TSV format containing the fields given in
   the ARDaC case audit template.

   Parameters
   ----------
   command_arguments : argparse.Namespace
      The command line arguments processed by argparse
   logger : logging.Logger
      The logger to be used to provide user feedback
   """
   template_path = Path(command_arguments.nodeTemplatesPath, _constants.demographic_template_file_name)
   dcc_subjects_path = Path(command_arguments.dccSubjectsFile)
   node_output_path = Path(command_arguments.nodeOutputPath)
   
   if not template_path.is_file():
      logger.critical('Cannot find demographic template file: ' + template_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path.as_posix())
   
   if not dcc_subjects_path.is_file():
      logger.critical('Cannot find DCC subjects file: ' + dcc_subjects_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_subjects_path.as_posix())
   
   if not node_output_path.is_dir():
      logger.critical('Cannot find node output directory: ' + node_output_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), node_output_path.as_posix())
   
   if command_arguments.subjectsType == 'observational':
      case_file_path = Path(node_output_path, _constants.case_obs_file_name)
   elif command_arguments.subjectsType == 'clinical':
      case_file_path = Path(node_output_path, _constants.case_rct_file_name)
   else:
      raise ValueError(f'Processing for subjects_type={command_arguments.subjectsType} is not implemented')

   if not case_file_path.is_file():
      logger.critical('Cannot find ARDaC case file: ' + case_file_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), case_file_path.as_posix())

   # Read the template TSV file to extract the headers
   logger.info(f'Reading demographic template CSV file: {template_path.as_posix()}')
   df_template = pd.read_csv(template_path.as_posix(), sep='\t', nrows=0)  # Read only the header
   template_headers = df_template.columns.tolist()  # Extract the headers as a list

   if command_arguments.subjectsType == 'observational':
      logger.info('Transforming observational subject data')
      node_file_path = Path(node_output_path, _constants.demographic_obs_file_name)
      df_obs_output = generate_observational_demographic_node(dcc_subjects_path, case_file_path, template_headers)
      df_obs_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Observational demographic node saved as: {node_file_path.as_posix()}')
   elif command_arguments.subjectsType == 'clinical':
      logger.info('Transforming clinical audit data')
      node_file_path = Path(node_output_path, _constants.demographic_rct_file_name)
      df_rct_output = generate_clinical_demographic_node(dcc_subjects_path, case_file_path, template_headers)
      df_rct_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Clinical demographic node saved as: {node_file_path.as_posix()}')
   else:
      raise ValueError(f'Processing for subjects_type={command_arguments.subjectsType} is not implemented')

if __name__ == '__main__':
   status = 0
   parser = argparse.ArgumentParser(
      description='''This utility generates ARDaC demographic nodes from observational or clinical trial DCC subject files and ARDaC case node files.
         The DCC subject files are provided in CSV format, and the ARDaC case node files are provided in ARDaC node TSV format.
         The user must provide the location of the ARDaC demographic node template file, the CSV file containing the DCC subject data,
         and the path to where the ARDaC demographic node file is to be written.''',
      epilog=f'''Observational case node files are named \'{_constants.case_obs_file_name}\'.
         Clinical case node files are named \'{_constants.case_rct_file_name}\'.  Demographic node files are written to the directory given by the --node_output_path argument.
         The ARDaC case node input TSV file is also expected to be at this location''')
   valid_log_level_names_mapping = logging.getLevelNamesMapping()
   valid_log_level_names_mapping.pop('NOTSET') # Remove NOTSET option value
   parser.add_argument('--version', action='version', version=f'DCC_VERSION={_constants.dcc_release_string},MAPPING_VERSION={_constants.mapping_version_string}')
   parser.add_argument('--dcc_version', action='version', version=f'{_constants.dcc_release_string}')
   parser.add_argument('--mapping_version', action='version', version=f'{_constants.mapping_version_string}')
   parser.add_argument('--log_level', dest='logLevel', default='INFO', choices=list(valid_log_level_names_mapping.keys()), help='A standard log level from the Python logger package')
   parser.add_argument('--node_templates_path', dest='nodeTemplatesPath', required=True, help='Path to the directory where the ARDaC node template TSV files are located')
   parser.add_argument('--subjects_type', dest='subjectsType', required=True, choices=['observational', 'clinical'], help='Value indicating if the input subject data is from clinical trial subjects or observational study subjects')
   parser.add_argument('--dcc_subjects_file', dest='dccSubjectsFile', required=True, help='Full path to the DCC input subjects file in CSV format')
   parser.add_argument('--node_output_path', dest='nodeOutputPath', required=True, help=f'''Path to the directory where the TSV audit node file is to be saved
                       -- the file name will be either {_constants.audit_obs_file_name} or {_constants.demographic_rct_file_name}.
                       This argument is also the expected location of the input ARDaC case node TSV file.''')

   parsed_args = parser.parse_args()
   
   # Configure and create logger for standard output
   console_handler = logging.StreamHandler(sys.stdout)
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
   except ValueError as e:
      logger.critical(f'Command line argument or parameter had a bad value: {e}')
   except Exception as e:
      logger.critical('Caught an exception', exc_info=True)
   
   exit(status)