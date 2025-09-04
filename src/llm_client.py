import os
import logging
import json
import openai
import google.generativeai as genai

class LLMClient:
    """
    An abstraction layer for interacting with Large Language Models (LLMs).
    It initializes clients for OpenAI and Google Gemini based on environment variables
    and implements a fallback mechanism from OpenAI to Gemini.
    """
    def __init__(self):
        """
        Initializes the LLM clients.
        It looks for 'OPENAI_API_KEY' and 'GOOGLE_API_KEY' in the environment.
        """
        self.openai_client = None
        self.gemini_client = None

        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            logging.info("OpenAI client initialized successfully.")
        else:
            logging.warning("OPENAI_API_KEY not found. OpenAI client not initialized.")

        # Initialize Gemini client
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-flash-latest')
            logging.info("Google Gemini client initialized successfully.")
        else:
            logging.warning("GOOGLE_API_KEY not found. Gemini client not initialized.")

        if not self.openai_client and not self.gemini_client:
            logging.error("No LLM clients could be initialized. Please set OPENAI_API_KEY or GOOGLE_API_KEY.")

    def call_llm(self, prompt: str, task: str) -> str:
        """
        Calls the LLM to perform a task, with a fallback from OpenAI to Gemini.

        Args:
            prompt (str): The full prompt to send to the LLM.
            task (str): The type of task ('extraction' or 'grouping'). This helps tailor the call.

        Returns:
            str: A JSON string representing the LLM's output.

        Raises:
            RuntimeError: If both OpenAI and Gemini clients fail or are not available.
        """
        # --- Primary: Try OpenAI ---
        if self.openai_client:
            try:
                logging.info("Attempting to call OpenAI API...")
                # Note: Using gpt-4o-mini as a fast and capable default.
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                response_content = response.choices[0].message.content
                logging.info("Successfully received response from OpenAI.")
                # Validate that the response is valid JSON
                json.loads(response_content)
                return response_content
            except Exception as e:
                logging.warning(f"OpenAI API call failed. Error: {e}. Attempting fallback to Gemini.")

        # --- Fallback: Try Gemini ---
        if self.gemini_client:
            try:
                logging.info("Attempting to call Google Gemini API...")
                # Gemini requires the prompt to explicitly ask for JSON output.
                gemini_prompt = f"{prompt}\n\nPlease provide the output in a valid JSON format."
                response = self.gemini_client.generate_content(gemini_prompt)

                # The response text might be wrapped in markdown, so we need to clean it.
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                logging.info("Successfully received response from Gemini.")
                # Validate that the cleaned response is valid JSON
                json.loads(response_text)
                return response_text
            except Exception as e:
                logging.error(f"Google Gemini API call also failed. Error: {e}")

        raise RuntimeError("Both OpenAI and Gemini LLM calls failed.")

# Global instance that can be imported by other modules
llm_client = LLMClient()
