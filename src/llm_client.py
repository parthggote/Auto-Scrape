import os
import logging
import json
import google.generativeai as genai

class LLMClient:
    """
    An abstraction layer for interacting with the Google Gemini Large Language Model.
    """
    def __init__(self):
        """
        Initializes the Gemini client.
        It looks for 'GOOGLE_API_KEY' in the environment.
        """
        self.gemini_client = None

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-flash-latest')
            logging.info("Google Gemini client initialized successfully.")
        else:
            logging.warning("GOOGLE_API_KEY not found. Gemini client not initialized.")
            # This will be caught by the MemoryManager or other components that need it.

    def call_llm(self, prompt: str, task: str) -> str:
        """
        Calls the Gemini LLM to perform a task.

        Args:
            prompt (str): The full prompt to send to the LLM.
            task (str): The type of task (e.g., 'grouping'). This helps tailor the call.

        Returns:
            str: A JSON string representing the LLM's output.

        Raises:
            RuntimeError: If the Gemini client is not available or the call fails.
        """
        if not self.gemini_client:
            raise RuntimeError("Gemini client is not initialized. Please set the GOOGLE_API_KEY.")

        try:
            logging.info(f"Attempting to call Google Gemini API for task: {task}...")
            # Gemini requires the prompt to explicitly ask for JSON output, which our prompts do.
            # The prompt already requests JSON, so we can send it directly.
            response = self.gemini_client.generate_content(prompt)

            # The response text might be wrapped in markdown ```json ... ```, so we need to clean it.
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            logging.info("Successfully received response from Gemini.")
            # Validate that the cleaned response is valid JSON before returning
            json.loads(response_text)
            return response_text

        except Exception as e:
            logging.error(f"Google Gemini API call failed. Error: {e}")
            # Log the full response if possible to debug invalid JSON issues
            if 'response' in locals():
                logging.error(f"Raw Gemini response text: {response.text}")
            raise RuntimeError("Google Gemini LLM call failed.") from e

# Global instance that can be imported by other modules
llm_client = LLMClient()
