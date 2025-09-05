import json
import logging
import os
from pathlib import Path

def build_master_schema(grouped_files_dir: str, output_path: str):
    """
    Merges all grouped schemas into a single master schema.

    This function scans a directory for individual grouped JSON files,
    reads them, and consolidates them into one comprehensive schema.

    Args:
        grouped_files_dir (str): The directory containing the grouped JSON files.
        output_path (str): The path to save the final master schema JSON.
    """
    logging.info(f"Starting master schema consolidation from directory '{grouped_files_dir}'...")

    master_schema = {
        "policy_info": {},
        "insured_party": {},
        "claim_details": {},
        "domain_specific": {},
        "metadata": {
            "source_files": []
        }
    }

    try:
        grouped_files = list(Path(grouped_files_dir).glob('*.json'))
        if not grouped_files:
            logging.warning(f"No grouped JSON files found in '{grouped_files_dir}'. Master schema will be empty.")
            # Still save the empty schema structure
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(master_schema, f, indent=2)
            return

        logging.info(f"Found {len(grouped_files)} grouped files to consolidate.")

        for grouped_file in grouped_files:
            with open(grouped_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # This logic is updated to handle the new ACORD-aware grouping structure.
                # It maps common ACORD object names to the master schema's sections.
                for category, group_object in data.items():
                    field_list = group_object.get("Fields", [])  # Safely get the list of fields

                    # Map new ACORD-style categories to the master schema sections
                    if category in ["Policy"]:
                        master_schema["policy_info"].update({f["field_name"]: f for f in field_list})
                    elif category in ["Insured", "Insured Pet", "Party", "Beneficiary", "Applicant Details"]:
                        master_schema["insured_party"].update({f["field_name"]: f for f in field_list})
                    elif category in ["Claim", "Treatment", "Amounts", "Payment", "Coverage", "Health History"]:
                        master_schema["claim_details"].update({f["field_name"]: f for f in field_list})
                    else:  # Address, Vehicle, Contact, etc. go here
                        master_schema["domain_specific"].update({f["field_name"]: f for f in field_list})

            master_schema["metadata"]["source_files"].append(grouped_file.name)

        with open(output_path, 'w') as f:
            json.dump(master_schema, f, indent=2)

        logging.info(f"Successfully built master schema and saved to '{output_path}'.")

    except Exception as e:
        logging.error(f"Failed to build the master schema. Error: {e}")
        raise
