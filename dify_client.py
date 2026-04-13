import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DifyClient:
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY")
        self.dataset_id = os.getenv("DIFY_DATASET_ID")
        self.base_url = "https://api.dify.ai/v1" # Change this if using self-hosted Dify
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_document(self, text, metadata=None):
        """
        Create a document in Dify Knowledge from text.
        """
        url = f"{self.base_url}/datasets/{self.dataset_id}/document/create_by_text"
        payload = {
            "text": text,
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "automatic"
            }
        }
        if metadata:
            # Dify might not support arbitrary metadata in create_by_text, 
            # but we can prepend it to the text or use it if the API supports it.
            # For now, we ensure the text contains the ID.
            pass
            
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_document(self, document_id, text):
        """
        Update an existing document in Dify Knowledge.
        """
        url = f"{self.base_url}/datasets/{self.dataset_id}/documents/{document_id}/update_by_text"
        payload = {
            "text": text
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
