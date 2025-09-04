import argparse
import json
import logging
import os
from pathlib import Path

# The following imports will be created in the next step.
# For now, this defines the required interface for our modules.
from src.scraper import scrape
from src.parser import parse
from src.extractor import extract_fields
from src.grouper import group_fields
from src.schema_builder import build_master_schema
from src.exporter import export_schema
from src.utils import setup_logging

# --- Directory and Path Constants ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
OUTPUTS_DIR = BASE_DIR / "outputs"
EXTRACTED_DIR = OUTPUTS_DIR / "extracted"
GROUPED_DIR = OUTPUTS_DIR / "grouped"
FINAL_DIR = OUTPUTS_DIR / "final"

def main(urls_path: str):
    """
    Main pipeline orchestrator.

    This function controls the entire workflow:
    1. Sets up logging and directories.
    2. Reads the list of forms to process.
    3. For each form, it calls the scraper, parser, extractor, and grouper.
    4. Consolidates all grouped schemas into a master schema.
    5. Exports the master schema to various formats.
    """
    setup_logging()
    logging.info("--- Starting the ACORD Insurance Form Analysis Pipeline ---")

    # 1. Ensure all necessary directories exist
    for dir_path in [RAW_DIR, PARSED_DIR, EXTRACTED_DIR, GROUPED_DIR, FINAL_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    logging.info("Verified that all data and output directories exist.")

    # 2. Load and validate the input URLs config file
    try:
        with open(urls_path, 'r') as f:
            forms_to_process = json.load(f)
        logging.info(f"Successfully loaded {len(forms_to_process)} forms to process from '{urls_path}'.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Fatal: Could not load or parse the URL config file at '{urls_path}'. Error: {e}")
        return

    # 3. Process each form sequentially
    for form_info in forms_to_process:
        try:
            region = form_info.get('region', 'UnknownRegion')
            insurer = form_info.get('insurer', 'UnknownInsurer')
            form_name = form_info.get('form_name', 'UnknownForm')
            url = form_info['url']
            doc_type = form_info['type']

            base_filename = f"{region}_{insurer}_{form_name}"
            logging.info(f"\n>>> Processing form: {base_filename} <<<")

            # --- Stage 1: Scraping ---
            raw_filepath = RAW_DIR / f"{base_filename}.{doc_type}"
            logging.info(f"[1/4] Scraping '{url}'...")
            scrape(url, str(raw_filepath), doc_type)

            # --- Stage 2: Parsing ---
            parsed_filepath = PARSED_DIR / f"{base_filename}.txt"
            logging.info(f"[2/4] Parsing '{raw_filepath.name}'...")
            parse(str(raw_filepath), str(parsed_filepath))

            # --- Stage 3: Field Extraction (AI) ---
            extracted_filepath = EXTRACTED_DIR / f"{base_filename}.json"
            logging.info(f"[3/4] Extracting fields from '{parsed_filepath.name}'...")
            extract_fields(str(parsed_filepath), str(extracted_filepath))

            # --- Stage 4: Field Grouping (AI) ---
            grouped_filepath = GROUPED_DIR / f"{base_filename}.json"
            logging.info(f"[4/4] Grouping fields from '{extracted_filepath.name}'...")
            group_fields(str(extracted_filepath), str(grouped_filepath))

            logging.info(f"--- Successfully processed {base_filename} ---")

        except KeyError as e:
            logging.error(f"Skipping form due to missing required key: {e} in {form_info}", exc_info=False)
        except Exception as e:
            logging.error(f"Failed to process form from URL '{form_info.get('url')}'. Error: {e}", exc_info=True)
            # Continue to the next form
            continue

    # 4. Consolidate all processed schemas
    logging.info("\n>>> Consolidating all schemas into a master schema <<<")
    master_schema_path = FINAL_DIR / "master_schema.json"
    build_master_schema(str(GROUPED_DIR), str(master_schema_path))

    # 5. Export the final schema in all required formats
    logging.info("\n>>> Exporting final master schema <<<")
    export_schema(str(master_schema_path), str(FINAL_DIR))

    logging.info("\n--- ACORD Insurance Form Analysis Pipeline finished successfully. ---")


if __name__ == "__main__":
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(
        description="ACORD Student Challenge 2025: Insurance Form Analysis Pipeline."
    )
    parser.add_argument(
        "urls_config",
        type=str,
        help="Path to the JSON configuration file containing the list of form URLs to process."
    )
    args = parser.parse_args()

    # Run the main pipeline
    main(args.urls_config)
