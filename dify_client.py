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
                    "chunk_length": 10000,
                    "chunk_overlap": 0
                },
                "pre_processing_rules": {
                    "remove_extra_spaces": True,
                    "remove_redundant_whitespace": True
                }
            },
            "doc_form": "text_model",
            "doc_language": "Vietnamese",
        }
        if metadata:
            pass
            
        print(f"Payload being sent to Dify: {payload}")
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 400:
            print(f"Dify API 400 Error Response: {response.text}")
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id):
        """
        Delete a document from Dify Knowledge.
        """
        url = f"{self.base_url}/datasets/{self.dataset_id}/documents/{document_id}"
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 400:
            print(f"Dify API 400 Error Response (Delete): {response.text}")
        response.raise_for_status()
        return response.json()
