import os
import sys
import errno
import argparse
import logging
import pandas as pd
from pathlib import Path
import _constants

def generate_observational_follow_up_node(obs_liver_scores_path: Path, obs_med_info_path: Path,  obs_vitals_path: Path, obs_soc_path: Path, obs_case_path: Path, template_headers: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
   """
   This function takes the path to the DCC observational liver scores, medical information, vitals,
   SOC, and the ARDaC observational case node files and the ARDaC follow-up template headers to
   generate the ARDaC observational follow-up node data.

   Parameters
   ----------
   obs_liver_scores_path : Path
      The full path to the DCC observational liver scores CSV file
   obs_med_info_path : Path
      The full path to the DCC observational medical information CSV file
   obs_vitals_path : Path
      The full path to the DCC observational vitals CSV file
   obs_soc_path : Path
      The full path to the DCC observational SOC CSV file
   obs_case_path : Path
      The full path to the ARDaC observational case node TSV file
   template_headers : list[str]
      The header names extracted from the ARDaC follow-up node template

   Return
   ------
   df_output : pd.DataFrame
      The observational follow-up node data
   df_qc : pd.DataFrame
      The observational follow-up QC data
   """
   # Define the extensions for mapping
   extensions = {"Week 0": "_0", "Week 4": "_28", "Week 12": "_84", "Week 24": "_168"}

   # Read the file using pandas
   logger.info(f'Reading the observational liver scores file: {obs_liver_scores_path.as_posix()}')
   df_obs_liver_scores_input = pd.read_csv(obs_liver_scores_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational liver scores file')

   logger.info(f'Reading the observational medical information file: {obs_med_info_path.as_posix()}')
   df_obs_med_info_input = pd.read_csv(obs_med_info_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational medical information file')

   logger.info(f'Reading the observational vitals file: {obs_vitals_path.as_posix()}')
   df_obs_vitals_input = pd.read_csv(obs_vitals_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational vitals file')

   logger.info(f'Reading the observational SOC file: {obs_soc_path.as_posix()}')
   df_obs_soc_input = pd.read_csv(obs_vitals_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading observational vitals file')

   logger.info(f'Reading the observational ARDaC case file: {obs_case_path.as_posix()}')
   df_obs_case_input = pd.read_csv(obs_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading observational case file')

   # Extract "*submitter_id" from df_obs_case and create case_table
   case_table = pd.DataFrame()
   case_table["*submitter_id"] = df_obs_case_input["*submitter_id"]
   case_table["usubjid"] = case_table["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"

   # Initialize the output DataFrame with the headers
   df_output = pd.DataFrame(columns=template_headers)

   for _, row in case_table.iterrows():
    submitter_id = row["*submitter_id"]

    for week, ext in extensions.items():
        new_row = {
            "*type": "follow_up",
            "project_id": "ARDaC-AlcHepNet",
            "*submitter_id": f"{submitter_id}{ext}",
            "cases.submitter_id": submitter_id,
            "demographics.submitter_id": f"{submitter_id}_demographic",
            "*days_to_follow_up": ext.lstrip("_"),  # Remove "_" from the extension
            "visit_day": ext.lstrip("_")
        }

        df_output = pd.concat([df_output, pd.DataFrame([new_row])], ignore_index=True)
   
   # Process the liver scores and map values to follow-up rows
   for _, row in df_obs_liver_scores_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions[redcap_event_name]
      submitter_id = f"{usubjid}_obs{extension}"

      # Find the matching row in df_output
      output_row_index = df_output[df_output["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output.loc[output_row_index, "meld_score"] = row.get("meld", None)
         df_output.loc[output_row_index, "child_pugh_score"] = row.get("cps", None)
         df_output.loc[output_row_index, "tlfb_drinking_days"] = row.get("tlfbnumdd", None)
         df_output.loc[output_row_index, "tlfb_number_drinks"] = row.get("tlfbnumd", None)
         df_output.loc[output_row_index, "liver_score_date"] = row.get("liverdat", None)

   # Process the medical information and map values to follow-up rows
   for _, row in df_obs_med_info_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions[redcap_event_name]
      submitter_id = f"{usubjid}_obs{extension}"

      # Find the matching row in df_output
      output_row_index = df_output[df_output["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output.loc[output_row_index, "ascites_culture"] = row.get("ascyn", None)
         df_output.loc[output_row_index, "hep_enceph"] = row.get("hepenyn", None)
         df_output.loc[output_row_index, "varices"] = row.get("varyn", None)
         df_output.loc[output_row_index, "hep_carcinoma"] = row.get("hepcaryn", None)
         df_output.loc[output_row_index, "liver_transplant"] = row.get("livtnsplyn", None)
         df_output.loc[output_row_index, "ascites_date"] = row.get("ascdat", None)
         df_output.loc[output_row_index, "hep_enceph_diagnosis_date"] = row.get("hependat", None)
         df_output.loc[output_row_index, "varices_diagnosis_date"] = row.get("vardat", None)
         df_output.loc[output_row_index, "hepcar_diagnosis_date"] = row.get("hepcardat", None)
         df_output.loc[output_row_index, "liver_transplant_date"] = row.get("livtnspldat", None)

   # Process the vitals and map values to follow-up rows
   for _, row in df_obs_vitals_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions[redcap_event_name]
      submitter_id = f"{usubjid}_obs{extension}"

      # Find the matching row in df_output
      output_row_index = df_output[df_output["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output.loc[output_row_index, "weight"] = row.get("weight", None)
         df_output.loc[output_row_index, "bmi"] = row.get("bmi", None)
   
   # Process the SOC and map values to follow-up rows
   for _, row in df_obs_soc_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions[redcap_event_name]
      submitter_id = f"{usubjid}_obs{extension}"

      # Find the matching row in df_output
      output_row_index = df_output[df_output["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output.loc[output_row_index, "infection_screen_done"] = row.get("infscreennd", None)
         df_output.loc[output_row_index, "infection_screen_date"] = row.get("infscreen_date", None)
         df_output.loc[output_row_index, "blood_culture"] = row.get("socisbcnd___999", None)
         df_output.loc[output_row_index, "blood_culture_result"] = row.get("socisbc", None)
         df_output.loc[output_row_index, "blood_organism"] = row.get("socisbc_pos", None)
         df_output.loc[output_row_index, "blood_culture_date"] = row.get("socisbcdat", None)
         df_output.loc[output_row_index, "urine_culture"] = row.get("socisucnd___999", None)
         df_output.loc[output_row_index, "urine_culture_result"] = row.get("socisuc", None)
         df_output.loc[output_row_index, "urine_culture_organism"] = row.get("socisuc_pos", None)
         df_output.loc[output_row_index, "urine_culture_date"] = row.get("socisucdat", None)
         df_output.loc[output_row_index, "urine_culture_fungal_result"] = row.get("soicuc_fung", None)
         df_output.loc[output_row_index, "ascites_culture"] = row.get("socisacnd___999", None)
         df_output.loc[output_row_index, "ascites_culture_result"] = row.get("socisac", None)
         df_output.loc[output_row_index, "ascites_organism"] = row.get("socisac_pos", None)
         df_output.loc[output_row_index, "ascites_date"] = row.get("socisacdat", None)
         df_output.loc[output_row_index, "endoscopy"] = row.get("endond", None)
         df_output.loc[output_row_index, "endoscopy_date"] = row.get("endodat", None)
         df_output.loc[output_row_index, "esophageal_varices_size"] = row.get("endovarsiz_esoph", None)
         df_output.loc[output_row_index, "esophageal_varices_bleed"] = row.get("endobled_esoph", None)
         df_output.loc[output_row_index, "gastric_varices_size"] = row.get("endovarsiz_gast", None)
         df_output.loc[output_row_index, "gastric_varices_bleed"] = row.get("endobled_gast", None)
         df_output.loc[output_row_index, "portal_hypertensive_gastropathy"] = row.get("porthypsev", None)
         df_output.loc[output_row_index, "esophageal_ulcer_size"] = row.get("endoulcsiz_esoph", None)
         df_output.loc[output_row_index, "esophageal_ulcer_bleed"] = row.get("endoulcbled_esoph", None)
         df_output.loc[output_row_index, "gastric_ulcer_size"] = row.get("endoulcsiz_gast", None)
         df_output.loc[output_row_index, "gastric_ulcer_bleed"] = row.get("endoulcbled_gast", None)
         df_output.loc[output_row_index, "duodenum_ulcer_size"] = row.get("endoulcsiz_duod", None)
         df_output.loc[output_row_index, "duodenum_ulcer_bleed"] = row.get("endoulcbled_duod", None)

   # Final check: Remove empty rows and log them in a QC file
   qc_records = []  # To store QC information for deleted rows

   # Columns that define a row as "non-empty" (exclude the fixed columns)
   non_empty_columns = list(set(df_output.columns) - {
      "*type", "project_id", "*submitter_id", "cases.submitter_id",
      "demographics.submitter_id", "*days_to_follow_up", "visit_day"
   })

   # Iterate over df_output rows to identify empty rows
   for index, row in df_output.iterrows():
      # Check if all non-fixed columns are empty
      if row[non_empty_columns].isnull().all():
         # Record the QC information
         qc_records.append({
            "usubjid": row["cases.submitter_id"].split("_")[0],  # Extract usubjid
            "*submitter_id": row["*submitter_id"],
            "empty_follow-up": "Y"
         })
         # Drop the empty row
         df_output.drop(index, inplace=True)

   # Save the QC records to a TSV file
   qc_output_path = "follow-up_qc_obs_DCC_data_release_v2-0-0.tsv"
   df_qc = pd.DataFrame(qc_records)

   return df_output, df_qc

def generate_clinical_follow_up_node(rct_liver_scores_path: Path, rct_med_info_path: Path,  rct_vitals_path: Path, rct_soc_path: Path, rct_case_path: Path, template_headers: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
   """
   This function takes the path to the DCC clinical liver scores, medical information, vitals,
   SOC, and the ARDaC clinical case node files and the ARDaC follow-up template headers to
   generate the clinical ARDaC follow-up node data.

   Parameters
   ----------
   obs_liver_scores_path : Path
      The full path to the DCC clinical liver scores CSV file
   obs_med_info_path : Path
      The full path to the DCC clinical medical information CSV file
   obs_vitals_path : Path
      The full path to the DCC clinical vitals CSV file
   obs_soc_path : Path
      The full path to the DCC clinical SOC CSV file
   obs_case_path : Path
      The full path to the ARDaC clinical case node TSV file
   template_headers : list[str]
      The header names extracted from the ARDaC follow-up node template

   Return
   ------
   df_output : pd.DataFrame
      The clinical follow-up node data
   df_qc : pd.DataFrame
      The clinical follow-up QC data
   """
   # Define the extensions for mapping
   extensions_rct = {"Day 0": "_0", "Day 3": "_3", "Day 7": "_7", "Day 14": "_14", "Day 28": "_28","Day 60": "_60","Day 90": "_90", "Day 180": "_180"}

   # Read the file using pandas
   logger.info(f'Reading the clinical liver scores file: {rct_liver_scores_path.as_posix()}')
   df_rct_liver_scores_input = pd.read_csv(rct_liver_scores_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical liver scores file')

   logger.info(f'Reading the clinical medical information file: {rct_med_info_path.as_posix()}')
   df_rct_med_info_input = pd.read_csv(rct_med_info_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical medical information file')

   logger.info(f'Reading the clinical vitals file: {rct_vitals_path.as_posix()}')
   df_rct_vitals_input = pd.read_csv(rct_vitals_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical vitals file')

   logger.info(f'Reading the clinical SOC file: {rct_soc_path.as_posix()}')
   df_rct_soc_input = pd.read_csv(rct_vitals_path.as_posix(), sep=',', dtype=str)
   logger.info(f'Done reading clinical vitals file')

   logger.info(f'Reading the clinical ARDaC case file: {rct_case_path.as_posix()}')
   df_rct_case_input = pd.read_csv(rct_case_path.as_posix(), sep='\t', dtype=str)
   logger.info(f'Done reading clinical case file')

   # Extract "*submitter_id" from df_obs_case and create case_table
   case_table_rct = pd.DataFrame()
   case_table_rct["*submitter_id"] = df_rct_case_input["*submitter_id"]
   case_table_rct["usubjid"] = case_table_rct["*submitter_id"].apply(lambda x: x.split("_")[0])  # Extract the number before "_"

   # Initialize the output DataFrame with the headers
   df_output_rct = pd.DataFrame(columns=template_headers)

   for _, row in case_table_rct.iterrows():
      submitter_id = row["*submitter_id"]

      for day, ext in extensions_rct.items():
         new_row = {
            "*type": "follow_up",
            "project_id": "ARDaC-AlcHepNet",
            "*submitter_id": f"{submitter_id}{ext}",
            "cases.submitter_id": submitter_id,
            "demographics.submitter_id": f"{submitter_id}_demographic",
            "*days_to_follow_up": ext.lstrip("_"),  # Remove "_" from the extension
            "visit_day": ext.lstrip("_")
         }
         
         df_output_rct = pd.concat([df_output_rct, pd.DataFrame([new_row])], ignore_index=True)

   # Process the liver scores and map values to follow-up rows
   for _, row in df_rct_liver_scores_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid Days
      if redcap_event_name not in extensions_rct:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions_rct[redcap_event_name]
      submitter_id = f"{usubjid}_clinical{extension}"

      # Find the matching row in df_output
      output_row_index = df_output_rct[df_output_rct["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output_rct.loc[output_row_index, "meld_score"] = row.get("meld", None)
         df_output_rct.loc[output_row_index, "child_pugh_score"] = row.get("cps", None)
         df_output_rct.loc[output_row_index, "tlfb_drinking_days"] = row.get("tlfbnumdd", None)
         df_output_rct.loc[output_row_index, "tlfb_number_drinks"] = row.get("tlfbnumd", None)
         df_output_rct.loc[output_row_index, "liver_score_date"] = row.get("liverdat", None)
   
   # JRM: This was commented out in the Python workbook for some reason
   # # Process the medinfo and map values to follow-up rows
   # for _, row in tqdm(df_med_info.iterrows(), total=len(df_med_info), desc="Processing MedInfo"):
   #     usubjid = row["usubjid"]
   #     redcap_event_name = row["redcap_event_name"]

   #     # Only process rows with valid weeks
   #     if redcap_event_name not in extensions_rct:
   #         continue

   #     # Convert redcap_event_name to the extension
   #     extension = extensions_rct[redcap_event_name]
   #     submitter_id = f"{usubjid}_clinical{extension}"

   #     # Find the matching row in df_output
   #     output_row_index = df_output[df_output["*submitter_id"] == submitter_id].index
   #     if not output_row_index.empty:
   #         # Perform the mapping
   #         output_row_index = output_row_index[0]  # Get the first matching index
   #         df_output.loc[output_row_index, "ascites_culture"] = row.get("ascyn", None)
   #         df_output.loc[output_row_index, "hep_enceph"] = row.get("hepenyn", None)
   #         df_output.loc[output_row_index, "varices"] = row.get("varyn", None)
   #         df_output.loc[output_row_index, "hep_carcinoma"] = row.get("hepcaryn", None)
   #         df_output.loc[output_row_index, "liver_transplant"] = row.get("livtnsplyn", None)
   #         df_output.loc[output_row_index, "ascites_date"] = row.get("ascdat", None)
   #         df_output.loc[output_row_index, "hep_enceph_diagnosis_date"] = row.get("hependat", None)
   #         df_output.loc[output_row_index, "varices_diagnosis_date"] = row.get("vardat", None)
   #         df_output.loc[output_row_index, "hepcar_diagnosis_date"] = row.get("hepcardat", None)
   #         df_output.loc[output_row_index, "liver_transplant_date"] = row.get("livtnspldat", None)

   # Process the vitals and map values to follow-up rows
   for _, row in df_rct_vitals_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions_rct:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions_rct[redcap_event_name]
      submitter_id = f"{usubjid}_clinical{extension}"

      # Find the matching row in df_output
      output_row_index = df_output_rct[df_output_rct["*submitter_id"] == submitter_id].index
      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output_rct.loc[output_row_index, "weight"] = row.get("weight", None)
         df_output_rct.loc[output_row_index, "bmi"] = row.get("bmi", None)

   # Process the SOC and map values to follow-up rows
   for _, row in df_rct_soc_input.iterrows():
      usubjid = row["usubjid"]
      redcap_event_name = row["redcap_event_name"]

      # Only process rows with valid weeks
      if redcap_event_name not in extensions_rct:
         continue

      # Convert redcap_event_name to the extension
      extension = extensions_rct[redcap_event_name]
      submitter_id = f"{usubjid}_clinical{extension}"

      # Find the matching row in df_output
      output_row_index = df_output_rct[df_output_rct["*submitter_id"] == submitter_id].index

      if not output_row_index.empty:
         # Perform the mapping
         output_row_index = output_row_index[0]  # Get the first matching index
         df_output_rct.loc[output_row_index, "infection_screen_done"] = row.get("infscreennd", None)
         df_output_rct.loc[output_row_index, "infection_screen_date"] = row.get("infscreen_date", None)
         df_output_rct.loc[output_row_index, "blood_culture"] = row.get("socisbcnd___999", None)
         df_output_rct.loc[output_row_index, "blood_culture_result"] = row.get("socisbc", None)
         df_output_rct.loc[output_row_index, "blood_organism"] = row.get("socisbc_pos", None)
         df_output_rct.loc[output_row_index, "blood_culture_date"] = row.get("socisbcdat", None)
         df_output_rct.loc[output_row_index, "urine_culture"] = row.get("socisucnd___999", None)
         df_output_rct.loc[output_row_index, "urine_culture_result"] = row.get("socisuc", None)
         df_output_rct.loc[output_row_index, "urine_culture_organism"] = row.get("socisuc_pos", None)
         df_output_rct.loc[output_row_index, "urine_culture_date"] = row.get("socisucdat", None)
         df_output_rct.loc[output_row_index, "urine_culture_fungal_result"] = row.get("soicuc_fung", None)
         df_output_rct.loc[output_row_index, "ascites_culture"] = row.get("socisacnd___999", None)
         df_output_rct.loc[output_row_index, "ascites_culture_result"] = row.get("socisac", None)
         df_output_rct.loc[output_row_index, "ascites_organism"] = row.get("socisac_pos", None)
         df_output_rct.loc[output_row_index, "ascites_date"] = row.get("socisacdat", None)
         df_output_rct.loc[output_row_index, "endoscopy"] = row.get("endond", None)
         df_output_rct.loc[output_row_index, "endoscopy_date"] = row.get("endodat", None)
         df_output_rct.loc[output_row_index, "esophageal_varices_size"] = row.get("endovarsiz_esoph", None)
         df_output_rct.loc[output_row_index, "esophageal_varices_bleed"] = row.get("endobled_esoph", None)
         df_output_rct.loc[output_row_index, "gastric_varices_size"] = row.get("endovarsiz_gast", None)
         df_output_rct.loc[output_row_index, "gastric_varices_bleed"] = row.get("endobled_gast", None)
         df_output_rct.loc[output_row_index, "portal_hypertensive_gastropathy"] = row.get("porthypsev", None)
         df_output_rct.loc[output_row_index, "esophageal_ulcer_size"] = row.get("endoulcsiz_esoph", None)
         df_output_rct.loc[output_row_index, "esophageal_ulcer_bleed"] = row.get("endoulcbled_esoph", None)
         df_output_rct.loc[output_row_index, "gastric_ulcer_size"] = row.get("endoulcsiz_gast", None)
         df_output_rct.loc[output_row_index, "gastric_ulcer_bleed"] = row.get("endoulcbled_gast", None)
         df_output_rct.loc[output_row_index, "duodenum_ulcer_size"] = row.get("endoulcsiz_duod", None)
         df_output_rct.loc[output_row_index, "duodenum_ulcer_bleed"] = row.get("endoulcbled_duod", None)

   # Final check: Remove empty rows and log them in a QC file
   qc_records_rct = []  # To store QC information for deleted rows

   # Columns that define a row as "non-empty" (exclude the fixed columns)
   non_empty_columns = list(set(df_output_rct.columns) - {
      "*type", "project_id", "*submitter_id", "cases.submitter_id",
      "demographics.submitter_id", "*days_to_follow_up", "visit_day"
   })

   # Iterate over df_output rows to identify empty rows
   for index, row in df_output_rct.iterrows():
      # Check if all non-fixed columns are empty
      if row[non_empty_columns].isnull().all():
         # Record the QC information
         qc_records_rct.append({
            "usubjid": row["cases.submitter_id"].split("_")[0],  # Extract usubjid
            "*submitter_id": row["*submitter_id"],
            "empty_follow-up": "Y"
         })

         # Drop the empty row
         df_output_rct.drop(index, inplace=True)

   # Save the QC records to a TSV file
   
   df_qc_rct = pd.DataFrame(qc_records_rct)

   return df_output_rct, df_qc_rct

   
def main(command_arguments: argparse.Namespace, logger: logging.Logger) -> int:
   """
   This function implements the steps needed for converting observational or clinical
   case data, liver scores, medical information, vitals, and SOC data into an ARDaC follow-up node.
   follow-up fields are determined by a provided ARDaC follow-up node template file.

   Parameters
   ----------
   command_arguments : argparse.Namespace
      The command line arguments processed by argparse
   logger : logging.Logger
      The logger to be used to provide user feedback
   """
   template_path = Path(command_arguments.nodeTemplatesPath, _constants.follow_up_template_file_name)
   dcc_liver_scores_path = Path(command_arguments.dccLiverScoresFile)
   dcc_med_info_path = Path(command_arguments.dccMedInfoFile)
   dcc_vitals_path = Path(command_arguments.dccVitalsFile)
   dcc_soc_path = Path(command_arguments.dccSOCFile)
   node_output_path = Path(command_arguments.nodeOutputPath)
   
   if not template_path.is_file():
      logger.critical('Cannot find follow-up template file: ' + template_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path.as_posix())
   
   if not dcc_liver_scores_path.is_file():
      logger.critical('Cannot find DCC liver scores file: ' + dcc_liver_scores_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_liver_scores_path.as_posix())
   
   if not dcc_med_info_path.is_file():
      logger.critical('Cannot find DCC medical information file: ' + dcc_med_info_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_med_info_path.as_posix())
   
   if not dcc_vitals_path.is_file():
      logger.critical('Cannot find DCC vitals file: ' + dcc_vitals_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_vitals_path.as_posix())
   
   if not dcc_soc_path.is_file():
      logger.critical('Cannot find DCC SOC file: ' + dcc_soc_path.as_posix())
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dcc_soc_path.as_posix())

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
   logger.info(f'Reading follow-up template CSV file: {template_path.as_posix()}')
   df_template = pd.read_csv(template_path.as_posix(), sep='\t', nrows=0)  # Read only the header
   template_headers = df_template.columns.tolist()  # Extract the headers as a list

   if command_arguments.subjectsType == 'observational':
      logger.info('Extracting observational follow-up data and creating ARDaC follow-up node')
      node_file_path = Path(node_output_path, _constants.follow_up_obs_file_name)
      node_file_qc_path = Path(node_output_path, _constants.follow_up_qc_obs_file_name)
      df_obs_output, df_qc_obs = generate_observational_follow_up_node(dcc_liver_scores_path, dcc_med_info_path,
                                                                       dcc_vitals_path, dcc_soc_path, case_file_path, template_headers)
      df_obs_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Observational follow-up node saved as: {node_file_path.as_posix()}')
      df_qc_obs.to_csv(node_file_qc_path.as_posix(), sep='\t', index=False, header=True)
      logger.info(f'Observational follow-up QC file saved as: {node_file_qc_path.as_posix()}')
   elif command_arguments.subjectsType == 'clinical':
      logger.info('Extracting clinical follow-up data and creating ARDaC follow-up node')
      node_file_path = Path(node_output_path, _constants.follow_up_rct_file_name)
      node_file_qc_path = Path(node_output_path, _constants.follow_up_qc_rct_file_name)
      df_rct_output, df_qc_rct = generate_clinical_follow_up_node(dcc_liver_scores_path, dcc_med_info_path,
                                                                  dcc_vitals_path, dcc_soc_path, case_file_path, template_headers)
      df_rct_output.to_csv(node_file_path.as_posix(), sep='\t', index=False, headers=True)
      logger.info(f'Clinical follow-up node saved as: {node_file_path.as_posix()}')
      df_qc_rct.to_csv(node_file_qc_path.as_posix(), sep='\t', index=False, headers=True)
      logger.info(f'Clinical QC file saved as: {node_file_qc_path.as_posix()}')
   else:
      raise ValueError(f'Processing for subjects_type={command_arguments.subjectsType} is not implemented')


if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      description='''This utility generates ARDaC follow-up nodes from ARDaC case nodes and observational or clinical trial DCC liver scores, medical information, vitals, and SOC data provided in CSV format files.
         The user must provide the location of the ARDaC follow-up node template file, the CSV files containing the DCC datasets, and the
         path to where the ARDaC follow-up node and quality control files are to be written.''',
      epilog=f'''Observational follow-up node files are named \'{_constants.follow_up_obs_file_name}\', and observational QC files are named \`{_constants.follow_up_qc_obs_file_name}.
         Clinical follow-up node files are named \'{_constants.follow_up_rct_file_name}\', and clinical QC files are named \'{_constants.follow_up_qc_rct_file_name}.  Node files are written to the directory given by the --node_output_path argument.
         The ARDaC case node input TSV file also expected to be at this location.''')
   valid_log_level_names_mapping = logging.getLevelNamesMapping()
   valid_log_level_names_mapping.pop('NOTSET') # Remove NOTSET option value
   parser.add_argument('--version', action='version', version=f'DCC_VERSION={_constants.dcc_release_string},MAPPING_VERSION={_constants.mapping_version_string}')
   parser.add_argument('--log_level', dest='logLevel', default='INFO', choices=list(valid_log_level_names_mapping.keys()), help='A standard log level from the Python logger package')
   parser.add_argument('--node_templates_path', dest='nodeTemplatesPath', required=True, help='Path to the directory where the ARDaC node template TSV files are located')
   parser.add_argument('--subjects_type', dest='subjectsType', required=True, choices=['observational', 'clinical'], help='Value indicating if the input subject data is from clinical trial subjects or observational study subjects')
   parser.add_argument('--dcc_liver_scores_file', dest='dccLiverScoresFile', required=True, help='Full path to the DCC input liver scores file in CSV format')
   parser.add_argument('--dcc_med_info_file', dest='dccMedInfoFile', required=True, help='Full path to the DCC input medical information file in CSV format')
   parser.add_argument('--dcc_vitals_file', dest='dccVitalsFile', required=True, help='Full path to the DCC input vitals file in CSV format')
   parser.add_argument('--dcc_soc_file', dest='dccSOCFile', required=True, help='Full path to the DCC input SOC file in CSV format')
   parser.add_argument('--node_output_path', dest='nodeOutputPath', required=True, help=f'Path to the directory where the TSV case node file is to be saved.  The file name will be either {_constants.case_obs_file_name} or {_constants.case_rct_file_name}')

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
   except ValueError as e:
      logger.critical(f'Command line argument or parameter had a bad value: {e}')
   except Exception as e:
      logger.critical('Caught an exception', exc_info=True)
   
   exit(status)