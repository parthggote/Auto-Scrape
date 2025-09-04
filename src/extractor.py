import json
import logging
from .llm_client import llm_client # Use a relative import

def extract_fields(parsed_text_path: str, output_path: str):
    """
    Extracts structured data fields from parsed text using an LLM.

    In this stub implementation, it uses the mock LLM client to generate
    a predefined set of extracted fields.

    Args:
        parsed_text_path (str): The path to the plain text file.
        output_path (str): The path to save the extracted fields as a JSON file.
    """
    logging.info(f"Reading parsed text from '{parsed_text_path}'...")

    try:
        with open(parsed_text_path, 'r') as f:
            text_content = f.read()

        # In a real implementation, this prompt would be carefully engineered.
        prompt = f"""
        You are analyzing an insurance form.
        Extract all data fields with field_name and description from the following text:
        ---
        {text_content}
        ---
        Return JSON like:
        [
          {{"field_name": "Pet Name", "description": "Name of insured pet"}},
          {{"field_name": "Owner Address", "description": "Full address of policyholder"}}
        ]
        """

        # Call the mock LLM client for the extraction task
        logging.info("Calling LLM for field extraction...")
        llm_response_str = llm_client.call_model(prompt, task='extraction')

        # The response is already a JSON string, so we just write it.
        # In a real scenario, you might want to parse and validate it first.
        with open(output_path, 'w') as f:
            f.write(llm_response_str)

        logging.info(f"Successfully extracted fields and saved to '{output_path}'.")

    except FileNotFoundError:
        logging.error(f"Parsed text file not found at '{parsed_text_path}'.")
        raise
    except Exception as e:
        logging.error(f"An error occurred during field extraction. Error: {e}")
        raise
