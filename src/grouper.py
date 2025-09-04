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
        with open(extracted_json_path, 'r', encoding='utf-8') as f:
            extracted_fields = json.load(f)

        # This prompt is engineered for modern LLMs to group fields effectively.
        prompt = f"""
        You are an expert insurance data architect. Your task is to group the following list of extracted form fields into logical categories.

        Use the following categories:
        - "Applicant Details"
        - "Pet Information"
        - "Health History"
        - "Coverage Selection"
        - "Payment Information"
        - "Other"

        Here is the list of fields to categorize:
        {json.dumps(extracted_fields, indent=2)}

        Return a single JSON object where each key is a category name and the value is a list of the fields belonging to that category. Do not create new categories.
        """

        # Call the LLM client for the grouping task
        logging.info("Calling LLM for field grouping...")
        llm_response_str = llm_client.call_llm(prompt, task='grouping')

        # The response from the new client is a JSON string.
        # We can do a quick validation and pretty-print it before saving.
        try:
            parsed_json = json.loads(llm_response_str)
            with open(output_path, 'w') as f:
                json.dump(parsed_json, f, indent=2)
        except json.JSONDecodeError:
            logging.error("LLM response was not valid JSON. Saving raw response.")
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
