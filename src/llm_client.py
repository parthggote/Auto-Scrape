import json
import logging

class LLMClient:
    """
    An abstraction layer for interacting with a Large Language Model (LLM).

    This client can be configured to use different backends like OpenAI, Ollama, etc.
    In this stub implementation, it does not make real API calls. Instead, it
    returns mock, hardcoded data to simulate the LLM's response for different tasks.
    """
    def __init__(self, config=None):
        """
        Initializes the LLM client.

        Args:
            config (dict, optional): Configuration for the LLM backend.
                                     For a real implementation, this would include
                                     API keys, model names, etc.
        """
        self.config = config
        logging.info("LLMClient initialized (mock mode).")

    def call_model(self, prompt: str, task: str) -> str:
        """
        Simulates a call to the LLM with a given prompt and task.

        Args:
            prompt (str): The full prompt to send to the LLM.
            task (str): The type of task ('extraction' or 'grouping').
                        This determines which mock response to return.

        Returns:
            str: A JSON string simulating the LLM's output.
        """
        logging.info(f"Simulating LLM call for task: '{task}'")

        if task == 'extraction':
            # Mock response for the 'extractor' module.
            mock_response = [
                {"field_name": "Pet Name", "description": "The name of the insured pet."},
                {"field_name": "Owner Full Name", "description": "Full legal name of the policyholder."},
                {"field_name": "Policy Number", "description": "The unique identifier for the insurance policy."},
                {"field_name": "Date of Birth", "description": "The pet's date of birth."},
                {"field_name": "Claim Amount", "description": "The total amount being claimed."},
            ]
        elif task == 'grouping':
            # Mock response for the 'grouper' module.
            mock_response = {
                "Applicant Details": [
                    {"field_name": "Owner Full Name", "description": "Full legal name of the policyholder."}
                ],
                "Pet Information": [
                    {"field_name": "Pet Name", "description": "The name of the insured pet."},
                    {"field_name": "Date of Birth", "description": "The pet's date of birth."}
                ],
                "Coverage Selection": [
                    {"field_name": "Policy Number", "description": "The unique identifier for the insurance policy."},
                    {"field_name": "Claim Amount", "description": "The total amount being claimed."}
                ],
                "Other": []
            }
        else:
            mock_response = {"error": "Unknown task type"}

        return json.dumps(mock_response, indent=2)

# Global instance that can be imported by other modules
llm_client = LLMClient()
