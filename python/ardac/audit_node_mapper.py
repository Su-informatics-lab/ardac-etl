import os
import sys
import errno
import argparse
import logging
import pandas as pd
from pathlib import Path
import _constants

def generate_observational_audit_node(obs_audit_path: Path, obs_case_path: Path, template_headers: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
   """
   This function takes the path to the DCC observational audit file, the ARDaC observational case node file,
   and the ARDaC audit node headers and produces the ARDaC audit node data for audit data that matches
   existing case data.  A file containing the subject ID's of case data that failed to match with
   audit data is also returned.

   Parameters
   ----------
   obs_audit_path : Path
      The full path to the DCC audit file for the DCC observational CSV file
   obs_case_path : Path
      The full path to the ARDaC case node file generated by case_node_mapper.py
   template_headers : list[str]
      The header names extracted from the ARDaC audit node template

   Return
   ------
   df_obs_output : pd.DataFrame
      The observational audit node data
   df_unmatched_obs : pd.DataFrame
      The subject IDs of the observational audit data that could not be matched to any
      case node data
   """
   # Read the file using pandas
   logger.info(f'Reading the observational audit file: {obs_audit_path.as_posix()}')
   df_obs_audit_input = pd.read_csv(obs_audit_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational audit file')

   logger.info(f'Reading the observational ARDaC case file: {obs_case_path.as_posix()}')
   df_obs_case_input = pd.read_csv(obs_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading observational case file')

   # Step 1: Extract "*submitter_id" from df_obs_case and create case_table
   case_table = pd.DataFrame()
   case_table["*submitter_id"] = df_obs_case_input["*submitter_id"]
   case_table["usubjid"] = case_table["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"
   df_obs_output = pd.DataFrame(index=case_table.index, columns=template_headers)

   # Initialize a list to store unmatched records
   unmatched_records_obs = []

   # Step 2: Iterate through case_table and map values to df_obs_output
   for _, row in case_table.iterrows():
      submitter_id = row["*submitter_id"]
      usubjid = row["usubjid"]

      # Find the corresponding record in df_obs_input
      input_row = df_obs_audit_input[df_obs_audit_input["usubjid"] == usubjid]
    
      if not input_row.empty:
         input_row = input_row.iloc[0]  # Extract the first matching row
         # Populate df_obs_output
         df_obs_output.loc[:, "*type"] = "audit"
         df_obs_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
         df_obs_output.loc[_, "*submitter_id"] = f"{submitter_id}_audit"
         df_obs_output.loc[_, "cases.submitter_id"] = f"{submitter_id}"
        
         df_obs_output.loc[_, "auditnd"] = input_row.get("auditnd", None)
         df_obs_output.loc[_, "adt0101"] = input_row.get("adt0101", None)
         df_obs_output.loc[_, "adt0102"] = input_row.get("adt0102", None)
         df_obs_output.loc[_, "adt0103"] = input_row.get("adt0103", None)
         df_obs_output.loc[_, "adt0104"] = input_row.get("adt0104", None)
         df_obs_output.loc[_, "adt0105"] = input_row.get("adt0105", None)
         df_obs_output.loc[_, "adt0106"] = input_row.get("adt0106", None)
         df_obs_output.loc[_, "adt0107"] = input_row.get("adt0107", None)
         df_obs_output.loc[_, "adt0108"] = input_row.get("adt0108", None)
         df_obs_output.loc[_, "adt0109"] = input_row.get("adt0109", None)
         df_obs_output.loc[_, "adt0110"] = input_row.get("adt0110", None)
      else:
         # Add unmatched record to the list
         unmatched_records_obs.append({
            "usubjid": usubjid,
            "*submitter_id": submitter_id,
            "missing_audit": "Y"
         })
         # Remove the unmatched row from df_rct_output
         df_obs_output.drop(_, inplace=True)
        
   # Step 3: QC Create a DataFrame for unmatched records
   df_unmatched_obs = pd.DataFrame(unmatched_records_obs)

   return df_obs_output, df_unmatched_obs


def generate_clinical_audit_node(rct_audit_path: Path, rct_case_path: Path, template_headers: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
   """
   This function takes the path to the DCC clinical audit file, the ARDaC clinical case node file,
   and the ARDaC audit node headers to produce the ARDaC audit node data for audit data that matches
   existing case data.  A file containing the subject ID's of case data that failed to match with
   audit data is also returned.

   Parameters
   ----------
   rct_audit_path : Path
      The full path to the audit file for the DCC clinical data
   rct_case_path : Path
      The full path to the ARDaC case node file generated by case_node_mapper.py
   template_headers : list[str]
      The header names extracted from the audit node template

   Return
   ------
   df_rct_output : pd.DataFrame
      The clinical audit node data
   df_unmatched_rct : pd.DataFrame
      The subject IDs of the clinical audit data that could not be matched to any
      case node data
   """
   # Read the file using pandas
   logger.info(f'Reading the clinical audit file: {rct_audit_path.as_posix()}')
   df_rct_audit_input = pd.read_csv(rct_audit_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical audit file')

   logger.info(f'Reading the observational ARDaC case file: {rct_case_path.as_posix()}')
   df_rct_case_input = pd.read_csv(rct_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading clinical case file')

   # Step 1: Extract "*submitter_id" from df_rct_case and create case_table
   case_table = pd.DataFrame()
   case_table["*submitter_id"] = df_rct_case_input["*submitter_id"]
   case_table["usubjid"] = case_table["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"
   df_rct_output = pd.DataFrame(index=case_table.index, columns=template_headers)

   # Initialize a list to store unmatched records
   unmatched_records_rct = []

   # Step 2: Iterate through case_table and map values to df_rct_output
   for _, row in case_table.iterrows():
      submitter_id = row["*submitter_id"]
      usubjid = row["usubjid"]

      # Find the corresponding record in df_rct_input
      input_row = df_rct_audit_input[df_rct_audit_input["usubjid"] == usubjid]
    
      if not input_row.empty:
         input_row = input_row.iloc[0]  # Extract the first matching row
         # Populate df_rct_output
         df_rct_output.loc[:, "*type"] = "audit"
         df_rct_output.loc[:, "project_id"] = "ARDaC-AlcHepNet"
         df_rct_output.loc[_, "*submitter_id"] = f"{submitter_id}_audit"
         df_rct_output.loc[_, "cases.submitter_id"] = f"{submitter_id}"
        
         df_rct_output.loc[_, "auditnd"] = input_row.get("auditnd", None)
         df_rct_output.loc[_, "adt0101"] = input_row.get("adt0101", None)
         df_rct_output.loc[_, "adt0102"] = input_row.get("adt0102", None)
         df_rct_output.loc[_, "adt0103"] = input_row.get("adt0103", None)
         df_rct_output.loc[_, "adt0104"] = input_row.get("adt0104", None)
         df_rct_output.loc[_, "adt0105"] = input_row.get("adt0105", None)
         df_rct_output.loc[_, "adt0106"] = input_row.get("adt0106", None)
         df_rct_output.loc[_, "adt0107"] = input_row.get("adt0107", None)
         df_rct_output.loc[_, "adt0108"] = input_row.get("adt0108", None)
         df_rct_output.loc[_, "adt0109"] = input_row.get("adt0109", None)
         df_rct_output.loc[_, "adt0110"] = input_row.get("adt0110", None)
      else:
         # Add unmatched record to the list
         unmatched_records_rct.append({
            "usubjid": usubjid,
            "*submitter_id": submitter_id,
            "missing_audit": "Y"
         })
         # Remove the unmatched row from df_rct_output
         df_rct_output.drop(_, inplace=True)
     
   # Step 3: QC Create a DataFrame for unmatched records
   df_unmatched_rct = pd.DataFrame(unmatched_records_rct)

   return df_rct_output, df_unmatched_rct


   
def main(command_arguments: argparse.Namespace, logger: logging.Logger) -> int:
   """
   This function implements the steps needed for converting observational or clinical
   audit and case data into an ARDaC audit node.  The audit data is provided in a CSV file
   and converted to an ARDaC audit node file in TSV format containing the fields given in
   the ARDaC audit template.

   Parameters
   ----------
   command_arguments : argparse.Namespace
      The command line arguments processed by argparse
   logger : logging.Logger
      The logger to be used to provide user feedback
   """
   template_path = Path(command_arguments.nodeTemplatesPath, _constants.audit_template_file_name)
   dcc_audit_path = Path(command_arguments.dccAuditFile)
   node_output_path = Path(command_arguments.nodeOutputPath)
   
   if not template_path.is_file():
      logger.critical('Cannot find audit template file: ' + template_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path.as_posix())
   
   if not dcc_audit_path.is_file():
      logger.critical('Cannot find DCC audit file: ' + dcc_audit_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_audit_path.as_posix())
   
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
   logger.info(f'Reading audit template CSV file: {template_path.as_posix()}')
   df_template = pd.read_csv(template_path.as_posix(), sep='\t', nrows=0)  # Read only the header
   template_headers = df_template.columns.tolist()  # Extract the headers as a list

   if command_arguments.subjectsType == 'observational':
      logger.info('Transforming observational audit data')
      node_file_path = Path(node_output_path, _constants.audit_obs_file_name)
      node_file_unmatched_path = Path(node_output_path, _constants.audit_obs_unmatched_file_name)
      df_obs_output, df_unmatched_obs = generate_observational_audit_node(dcc_audit_path, case_file_path, template_headers)
      df_obs_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Observational audit node saved as: {node_file_path.as_posix()}')
      df_unmatched_obs.to_csv(node_file_unmatched_path, sep='\t', index=False)
      logger.info(f'Observational QC file saved as: {node_file_unmatched_path.as_posix()}')
   elif command_arguments.subjectsType == 'clinical':
      logger.info('Transforming clinical audit data')
      node_file_path = Path(node_output_path, _constants.audit_rct_file_name)
      node_file_unmatched_path = Path(node_output_path, _constants.audit_rct_unmatched_file_name)
      df_rct_output, df_unmatched_rct = generate_clinical_audit_node(dcc_audit_path, case_file_path, template_headers)
      df_rct_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Clinical audit node saved as: {node_file_path.as_posix()}')
      df_unmatched_rct.to_csv(node_file_unmatched_path.as_posix(), sep='\t', index=False)
      logger.info(f'Clinical QC file saved as: {node_file_unmatched_path.as_posix()}')
   else:
      raise ValueError(f'Processing for subjects_type={command_arguments.subjectsType} is not implemented')
   
   return 0


if __name__ == '__main__':
   status = 0
   parser = argparse.ArgumentParser(
      description='''This utility generates ARDaC audit nodes from observational or clinical trial DCC audit files and ARDaC case node files.
         The DCC audit files are provided in CSV format, and the ARDaC case node files are provided in ARDaC node TSV format.
         The user must provide the location of the ARDaC audit node template file, the CSV file containing the DCC audit data,
         and the path to where the ARDaC audit node and quality control files are to be written.''',
      epilog=f'''Observational audit node files are named \'{_constants.audit_obs_file_name}\', and observational QC files are named \'{_constants.audit_obs_unmatched_file_name}\'.
         Clinical audit node files are named \'{_constants.audit_rct_file_name}\', and clinical QC files are named \'{_constants.audit_rct_unmatched_file_name}\'.  Audit node files are written to the directory given by the --node_output_path argument.
         The ARDaC case node input TSV file is also expected to be at this location''')
   valid_log_level_names_mapping = logging.getLevelNamesMapping()
   valid_log_level_names_mapping.pop('NOTSET') # Remove NOTSET option value
   parser.add_argument('--version', action='version', version=f'DCC_VERSION={_constants.dcc_release_string},MAPPING_VERSION={_constants.mapping_version_string}')
   parser.add_argument('--dcc_version', action='version', version=f'{_constants.dcc_release_string}')
   parser.add_argument('--mapping_version', action='version', version=f'{_constants.mapping_version_string}')
   parser.add_argument('--log_level', dest='logLevel', default='INFO', choices=list(valid_log_level_names_mapping.keys()), help='A standard log level from the Python logger package')
   parser.add_argument('--node_templates_path', dest='nodeTemplatesPath', required=True, help='Path to the directory where the ARDaC node template TSV files are located')
   parser.add_argument('--subjects_type', dest='subjectsType', required=True, choices=['observational', 'clinical'], help='Value indicating if the input subject data is from clinical trial subjects or observational study subjects')
   parser.add_argument('--dcc_audit_file', dest='dccAuditFile', required=True, help='Full path to the DCC input audit file in CSV format')
   parser.add_argument('--node_output_path', dest='nodeOutputPath', required=True, help=f'''Path to the directory where the TSV audit node file is to be saved
                       -- the file name will be either {_constants.audit_obs_file_name} or {_constants.audit_rct_file_name}.
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