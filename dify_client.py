import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DifyClient:
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY")
        self.workflow_api_key = os.getenv("DIFY_WORKFLOW_API_KEY", self.api_key)
        self.user_id = os.getenv("DIFY_USER_ID", "service_desk_sync_bot")
        self.dataset_id = os.getenv("DIFY_DATASET_ID")
        self.base_url = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
        
        # Debug: Print first 4 chars of API key to verify loading
        if self.api_key:
            print(f"Dify API Key loaded: {self.api_key[:4]}****")
        else:
            print("Dify API Key NOT loaded!")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.workflow_headers = {
            "Authorization": f"Bearer {self.workflow_api_key}",
            "Content-Type": "application/json"
        }

    def upload_file(self, file_path, filename):
        """
        Uploads a file to Dify and returns the file_id.
        """
        url = f"{self.base_url}/files/upload"
        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            # Note: files parameter in requests overrides the Content-Type header
            response = requests.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, files=files)
            response.raise_for_status()
            return response.json().get("id")

    def run_workflow(self, filename, file_id):
        """
        Triggers the Dify Workflow to process the uploaded file.
        """
        url = f"{self.base_url}/workflows/run"
        payload = {
            "inputs": {
                "filename": filename,
                "file": {
                    "type": "document",
                    "transfer_method": "local_file",
                    "upload_file_id": file_id
                }
            },
            "response_mode": "blocking",
            "user": self.user_id
        }
        response = requests.post(url, json=payload, headers=self.workflow_headers)
        response.raise_for_status()
        return response.json()
