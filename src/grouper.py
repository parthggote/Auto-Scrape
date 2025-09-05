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
You are an expert insurance data architect familiar with ACORD data modeling and object-based standards.

Task:
Group the following extracted fields into natural, human-readable categories that represent domain objects (for example: Policy, Insured, Party, Address, Contact, Claim, Coverage, Vehicle, Treatment, Amounts). Do NOT use a fixed set of categories — create group names that best reflect the data provided.

Design goals and constraints:
- Prefer ACORD-style object names when they naturally match the fields (e.g., "Policy", "Insured", "Claim", "Address"). Use examples only as guidance; you are free to create appropriate group names if the data suggests a different object (e.g., "Vehicle", "Beneficiary").
- Each field must belong to exactly one group.
- Groups names should be concise (1–3 words).
- Avoid creating an "Other" group unless truly necessary.
- Output MUST be valid JSON only. Do not write explanatory text.

Additional accuracy guidelines:
1. **Preserve semantic meaning**: Do not rename field labels; return `field_name` exactly as provided.
2. **Prioritize ACORD object hierarchy**: Where possible, align groups to ACORD’s known objects (Policy, Party, Insured, Claim, Coverage, Premium, Vehicle, Risk, Payment, Contact, Address, Amounts, Codes).
3. **Consistency across forms**: If two fields from different forms represent the same logical concept (e.g., "DOB", "Date of Birth"), group them under the same object name (e.g., Party/Insured).
4. **Disambiguation rule**: If a field could belong to multiple objects, choose the *most specific object* (e.g., “Vehicle VIN” → Vehicle, not Policy).
5. **Granularity rule**: Do not collapse unrelated fields into one broad group. Keep groups focused (e.g., separate "Address" from "Contact").
6. **Datatype accuracy**: Always infer and provide `suggested_datatype` realistically:
   - Dates → `date`
   - Identifiers (Policy Number, Claim Number) → `string`
   - Money amounts → `currency`
   - Boolean (Yes/No, true/false) → `boolean`
   - Enumerations (State, Gender, Currency) → `code`
   - Others default → `string`
7. **Code list hints**: If the field clearly maps to a common ACORD code list, provide a short identifier:
   - U.S. States → `"StateCode"`
   - ISO currencies → `"CurrencyCode"`
   - Gender → `"GenderCode"`
   - Relationship → `"RelationshipCode"`
   - Otherwise → `null`
8. **Group ordering**: Place high-level groups (Policy, Insured, Claim, Coverage) before detail groups (Address, Contact, Payment).
9. **Traceability**: Include `acord_object_hint` for every field. If uncertain, provide your *best guess* (e.g., "Policy/PolicyNumber").
10. **No duplication**: Do not repeat the same field under multiple groups.
11. **Minimal nesting**: Only use one level of groups (no group-inside-group). ACORD alignment can happen via `acord_object_hint`.

For each field, return:
- `field_name` (original text)
- `description` (original text)
- `acord_object_hint` (short ACORD-like object path or null)
- `suggested_datatype` (see rules above)
- `suggested_code_list` (short list name or null)

Output schema (strictly follow this JSON shape):
{{
  "<GroupName>": {{
    "Fields": [
      {{
        "field_name": "<original field label>",
        "description": "<original description>",
        "acord_object_hint": "<optional short hint or null>",
        "suggested_datatype": "<string|integer|number|boolean|date|datetime|currency|code>",
        "suggested_code_list": "<optional code list name or null>"
      }},
      ...
    ]
  }},
  ...
}}

Here are the fields to categorize:
{json.dumps(extracted_fields, indent=2)}
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
