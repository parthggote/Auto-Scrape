import json
import logging
from .llm_client import llm_client # Use a relative import

def group_fields(extracted_json_path: str, output_path: str):
    """
    Groups extracted fields into logical categories using an LLM.

    In this stub implementation, it uses the mock LLM client to generate
    a predefined, grouped structure.

    Args:
        extracted_json_path (str): The path to the JSON file with extracted fields.
        output_path (str): The path to save the grouped fields as a new JSON file.
    """
    logging.info(f"Reading extracted fields from '{extracted_json_path}'...")

    try:
        with open(extracted_json_path, 'r') as f:
            extracted_fields = json.load(f)

        # In a real implementation, this prompt would be carefully engineered.
        prompt = f"""
        You are an insurance data architect. Group the following extracted fields
        into logical blocks:
        - Applicant Details
        - Pet Information
        - Health History
        - Coverage Selection
        - Payment Information
        - Other/Region-Specific

        Fields to group:
        {json.dumps(extracted_fields, indent=2)}

        Return a single JSON object where keys are the group names.
        """

        # Call the mock LLM client for the grouping task
        logging.info("Calling LLM for field grouping...")
        llm_response_str = llm_client.call_model(prompt, task='grouping')

        # The response is already a JSON string, so we just write it.
        with open(output_path, 'w') as f:
            f.write(llm_response_str)

        logging.info(f"Successfully grouped fields and saved to '{output_path}'.")

    except FileNotFoundError:
        logging.error(f"Extracted fields JSON not found at '{extracted_json_path}'.")
        raise
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON from '{extracted_json_path}'.")
        raise
    except Exception as e:
        logging.error(f"An error occurred during field grouping. Error: {e}")
        raise
