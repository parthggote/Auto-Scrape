import json
import logging
from .llm_client import llm_client
from .memory_manager import MemoryManager

def build_rag_prompt(fields_to_group: list, similar_examples: dict) -> str:
    """Builds the prompt for the LLM, including RAG context."""

    # Format the RAG examples for the prompt
    rag_context_str = "No similar fields found in memory."
    if similar_examples:
        rag_context_str = "To ensure consistency, please use the following examples of previously grouped fields as a reference. Pay close attention to the `group_name` and `acord_object_hint` used for fields similar to the ones below:\n\n"
        for field_name, examples in similar_examples.items():
            if examples:
                rag_context_str += f"For a field like '{field_name}', consider these past groupings:\n"
                for ex in examples:
                    rag_context_str += f"- Past Field: '{ex['field_name']}' -> Group: '{ex['group_name']}', Hint: '{ex['acord_object_hint']}'\n"
                rag_context_str += "\n"

    # The main prompt structure, now including a placeholder for RAG context
    prompt = f"""
You are an expert insurance data architect familiar with ACORD data modeling and object-based standards, with a niche focus on Pet Insurance.

### Task
Group the following extracted fields into natural, human-readable categories that represent domain objects (e.g., Policy, Insured, Pet, Address, Contact, Claim, Coverage, Treatment, Amounts). Create new, logical group names if the data requires it.

### Design Goals and Constraints
- Each field must belong to exactly one group.
- Group names should be concise (1–3 words).
- Prefer ACORD-style object names where natural.
- **CRITICAL**: Preserve the `field_name` exactly as provided in the input.

### Memory & Consistency (Soft Memory / RAG)
{rag_context_str}

### Extended Accuracy Guidelines
1.  **Preserve semantic meaning**: Do not rename field labels; return `field_name` exactly as provided.
2.  **Prioritize ACORD hierarchy**: Align groups to ACORD’s known objects where possible.
3.  **Consistency across forms**: Use the provided examples to normalize fields with similar meanings into the same logical group.
4.  **Disambiguation rule**: Choose the *most specific object* (e.g., "Pet Microchip ID" → PetIdentification, not Policy).
5.  **Datatype accuracy**: Infer `suggested_datatype` (date, string, currency, boolean, code).
6.  **Code list hints**: For fields like State or Gender, set `suggested_code_list` to a hint like "StateCode" or "GenderCode"; otherwise, `null`.
7.  **Traceability**: Provide a best-guess `acord_object_hint` for every field (e.g., `"Policy/PolicyNumber"`).

### Output Schema (Strict JSON only)
Provide your response as a single JSON object. Do not include any explanatory text outside the JSON structure.
{{
  "<GroupName>": {{
    "Fields": [
      {{
        "field_name": "<original field label>",
        "description": "<original description>",
        "acord_object_hint": "<optional short hint or null>",
        "suggested_datatype": "<string|integer|number|boolean|date|datetime|currency|code>",
        "suggested_code_list": "<optional code list name or null>"
      }}
    ]
  }}
}}

### Fields to Categorize
Group ONLY the fields listed below. Do not invent new fields.
{json.dumps(fields_to_group, indent=2)}
"""
    return prompt

def group_fields(extracted_json_path: str, output_path: str, memory_manager: MemoryManager):
    """
    Groups extracted fields using a hybrid approach of dictionary mapping and RAG-powered LLM calls.
    """
    logging.info(f"Starting hybrid field grouping for '{extracted_json_path}'.")

    try:
        with open(extracted_json_path, 'r', encoding='utf-8') as f:
            raw_fields = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Could not read or parse extracted fields from '{extracted_json_path}'. Error: {e}")
        raise

    # --- Normalization Step ---
    # Ensure all fields are in the expected dict format, handling cases where the input is a list of strings.
    extracted_fields = []
    for field in raw_fields:
        if isinstance(field, str):
            # If the item is just a string, convert it to the dict structure.
            extracted_fields.append({"field_name": field, "description": ""})
        elif isinstance(field, dict) and "field_name" in field:
            # If it's already a dict with the required key, use it as is.
            extracted_fields.append(field)
    logging.info(f"Normalized {len(raw_fields)} raw fields into {len(extracted_fields)} structured fields.")

    grouped_results = {}
    fields_to_process_with_llm = []
    rag_examples = {}

    # Step 1: Dictionary Lookup (Hard Memory)
    for field in extracted_fields:
        field_name = field.get("field_name")
        if not field_name:
            continue

        if field_name in memory_manager.dictionary:
            mapping = memory_manager.dictionary[field_name]
            group_name = mapping["group_name"]

            if group_name not in grouped_results:
                grouped_results[group_name] = {"Fields": []}

            # Create the field structure for the output
            grouped_field = {
                "field_name": field_name,
                "description": field.get("description"),
                "acord_object_hint": mapping.get("acord_object_hint"),
                "suggested_datatype": "string", # Default, can be improved
                "suggested_code_list": None
            }
            grouped_results[group_name]["Fields"].append(grouped_field)
            logging.info(f"Field '{field_name}' grouped using dictionary to '{group_name}'.")
        else:
            fields_to_process_with_llm.append(field)

    # Step 2: RAG + LLM for remaining fields
    if fields_to_process_with_llm:
        logging.info(f"{len(fields_to_process_with_llm)} fields not found in dictionary, processing with LLM.")

        # Gather RAG context for all fields that need processing
        for field in fields_to_process_with_llm:
            field_name = field["field_name"]
            similar = memory_manager.find_similar_fields(field_name)
            if similar:
                rag_examples[field_name] = similar

        # Build the prompt with all remaining fields and RAG context
        prompt = build_rag_prompt(fields_to_process_with_llm, rag_examples)

        try:
            llm_response_str = llm_client.call_llm(prompt, task='grouping')
            llm_grouped_data = json.loads(llm_response_str)

            # Step 3: Merge LLM results and update memory
            for group_name, group_data in llm_grouped_data.items():
                if group_name not in grouped_results:
                    grouped_results[group_name] = {"Fields": []}

                for field in group_data.get("Fields", []):
                    grouped_results[group_name]["Fields"].append(field)

                    # Update memory with the new mapping
                    field_name = field.get("field_name")
                    acord_hint = field.get("acord_object_hint")
                    if field_name and group_name and acord_hint:
                        memory_manager.add_new_mapping(field_name, group_name, acord_hint)

            logging.info("Successfully processed remaining fields with LLM and updated memory.")

        except json.JSONDecodeError as e:
            logging.error(f"LLM response was not valid JSON. Cannot process. Error: {e}. Raw response: {llm_response_str}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during LLM call or processing. Error: {e}")

    # Save the final combined results
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(grouped_results, f, indent=2)
        logging.info(f"Successfully saved final grouped fields to '{output_path}'.")
    except Exception as e:
        logging.error(f"Failed to save final grouped output. Error: {e}")
        raise
