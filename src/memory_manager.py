import json
import logging
from pathlib import Path
import os
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient, models

# --- Constants ---
MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"
DICTIONARY_PATH = MEMORY_DIR / "field_to_group_dictionary.json"
QDRANT_PATH = str(MEMORY_DIR / "qdrant_db")
COLLECTION_NAME = "insurance_form_fields"

class MemoryManager:
    """
    Manages the persistent memory for the grouping process.
    This includes a dictionary for exact matches (hard memory) and a Qdrant
    vector store for similarity-based lookups (soft memory).
    """

    def __init__(self):
        """Initializes the MemoryManager, loading existing data if available."""
        logging.info("Initializing MemoryManager...")
        MEMORY_DIR.mkdir(exist_ok=True)

        self.dictionary = self._load_dictionary()

        # Ensure GOOGLE_API_KEY is set
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        self.qdrant_client = QdrantClient(path=QDRANT_PATH)

        self.vector_store = Qdrant(
            client=self.qdrant_client,
            collection_name=COLLECTION_NAME,
            embeddings=self.embeddings,
        )

        # Ensure the collection exists
        self._ensure_collection_exists()

        logging.info(f"MemoryManager initialized. Dictionary has {len(self.dictionary)} entries.")

    def _load_dictionary(self) -> dict:
        """Loads the field-to-group dictionary from a JSON file."""
        if DICTIONARY_PATH.exists():
            logging.info(f"Loading existing dictionary from {DICTIONARY_PATH}")
            with open(DICTIONARY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logging.info("No existing dictionary found. Starting with an empty one.")
            return {}

    def _save_dictionary(self):
        """Saves the current dictionary to a JSON file."""
        logging.info(f"Saving dictionary with {len(self.dictionary)} entries to {DICTIONARY_PATH}")
        with open(DICTIONARY_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, indent=2)

    def _ensure_collection_exists(self):
        """Checks if the Qdrant collection exists and creates it if not."""
        try:
            self.qdrant_client.get_collection(collection_name=COLLECTION_NAME)
            logging.info(f"Qdrant collection '{COLLECTION_NAME}' already exists.")
        except Exception:
            logging.info(f"Creating new Qdrant collection: '{COLLECTION_NAME}'")
            self.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )

    def add_new_mapping(self, field_name: str, group_name: str, acord_hint: Optional[str]):
        """
        Adds a new field-to-group mapping to both the dictionary and the vector store.
        """
        if field_name in self.dictionary:
            return # Already exists

        # 1. Update dictionary
        self.dictionary[field_name] = {
            "group_name": group_name,
            "acord_object_hint": acord_hint
        }
        self._save_dictionary()

        # 2. Update vector store
        # We use the field name as the document content to be embedded.
        # Metadata will store the grouping information.
        self.vector_store.add_texts(
            [field_name],
            metadatas=[{"group_name": group_name, "acord_object_hint": acord_hint}],
        )
        logging.info(f"Added new mapping for '{field_name}' to group '{group_name}'.")

    def find_similar_fields(self, field_name: str, top_k: int = 5) -> list[dict]:
        """
        Finds the most similar fields from the vector store.

        Args:
            field_name (str): The name of the field to search for.
            top_k (int): The number of similar fields to return.

        Returns:
            A list of dictionaries, where each dictionary contains the
            'field_name', 'group_name', and 'acord_object_hint' of a similar field.
        """
        if not self.qdrant_client.count(collection_name=COLLECTION_NAME, exact=False).count > 0:
            logging.warning("Vector store is empty. Cannot find similar fields.")
            return []

        try:
            results = self.vector_store.similarity_search_with_score(field_name, k=top_k)

            similar_fields = []
            for doc, score in results:
                similar_fields.append({
                    "field_name": doc.page_content,
                    "group_name": doc.metadata.get("group_name", "Unknown"),
                    "acord_object_hint": doc.metadata.get("acord_object_hint", "null"),
                    "similarity_score": score
                })
            logging.info(f"Found {len(similar_fields)} similar fields for '{field_name}'.")
            return similar_fields
        except Exception as e:
            logging.error(f"Error during similarity search for '{field_name}': {e}")
            return []
