import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DifyClient:
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY")
        self.dataset_id = os.getenv("DIFY_DATASET_ID")
        self.base_url = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_document(self, text, title, metadata=None):
        """
        Create a document in Dify Knowledge from text.
        Each ticket is pushed as a single chunk.
        """
        url = f"{self.base_url}/datasets/{self.dataset_id}/document/create_by_text"
        payload = {
            "name": title,
            "text": text,
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "custom",
                "rules": {
                    "chunk_length": 100000,
                    "chunk_overlap": 0
                }
            },
            "doc_form": "text_model",
            "doc_language": "Vietnamese",
        }
        if metadata:
            pass
            
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 400:
            print(f"Dify API 400 Error Response: {response.text}")
        response.raise_for_status()
        return response.json()

    def update_document(self, document_id, text, name):
        """
        Update an existing document in Dify Knowledge.
        Each ticket is updated as a single chunk.
        """
        url = f"{self.base_url}/datasets/{self.dataset_id}/documents/{document_id}/update_by_text"
        payload = {
            "name": name,
            "text": text,
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "custom",
                "rules": {
                    "chunk_length": 100000,
                    "chunk_overlap": 0
                }
            }
        }
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 400:
            print(f"Dify API 400 Error Response (Update): {response.text}")
        response.raise_for_status()
        return response.json()
