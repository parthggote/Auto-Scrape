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
        # Explicitly open the file with UTF-8 encoding to prevent errors.
        with open(parsed_text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()

        # This prompt is engineered to be effective with modern LLMs.
        prompt = f"""
        You are an expert data extraction assistant. Your task is to analyze the text from an insurance form below and extract all data entry fields.
        For each field, provide a concise 'field_name' and a brief 'description'.
        Return the result as a single JSON object where the key is "fields" and the value is a list of objects.

        Example Format:
        {{
          "fields": [
            {{"field_name": "Pet Name", "description": "The name of the insured pet"}},
            {{"field_name": "Owner Address", "description": "The full address of the policyholder"}}
          ]
        }}

        Analyze the following text:
        ---
        {text_content}
        ---
        """

        # Call the LLM client for the extraction task
        logging.info("Calling LLM for field extraction...")
        llm_response_str = llm_client.call_llm(prompt, task='extraction')

        # The response from the new client is a JSON string.
        # We can do a quick validation and pretty-print it before saving.
        try:
            parsed_json = json.loads(llm_response_str)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, indent=2)
        except json.JSONDecodeError:
            logging.error("LLM response was not valid JSON. Saving raw response.")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(llm_response_str)

        logging.info(f"Successfully extracted fields and saved to '{output_path}'.")

    except FileNotFoundError:
        logging.error(f"Parsed text file not found at '{parsed_text_path}'.")
        raise
    except Exception as e:
        logging.error(f"An error occurred during field extraction. Error: {e}")
        raise
