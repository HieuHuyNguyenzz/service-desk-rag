import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

class JiraClient:
    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.headers = {"Accept": "application/json"}

    def get_tickets(self, project_key, updated_since=None):
        """
        Fetch tickets from a Jira project.
        updated_since: date string (e.g., '2023-01-01') to filter updates.
        """
        jql = f'project = "{project_key}"'
        if updated_since:
            jql += f' AND updated >= "{updated_since}"'
        
        tickets = []
        start_at = 0
        max_results = 50

        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": "summary,description,comment,updated,created"
            }
            response = requests.get(f"{self.url}/rest/api/3/search", params=params, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("issues", [])
            if not issues:
                break
                
            tickets.extend(issues)
            start_at += len(issues)
            if start_at >= data.get("total", 0):
                break
                
        return tickets

    def format_ticket(self, issue):
        """Format ticket data into a string for Dify knowledge."""
        fields = issue.get("fields", {})
        summary = fields.get("summary", "No Summary")
        description = fields.get("description", "No Description")
        # Description in Jira API v3 is often ADF (Atlassian Document Format), we might need to simplify it.
        if isinstance(description, dict):
            description = self._extract_text_from_adf(description)
            
        comments = fields.get("comment", {}).get("comments", [])
        comments_text = "\n".join([self._extract_text_from_adf(c.get("body", "")) if isinstance(c.get("body"), dict) else c.get("body", "") for c in comments])
        
        ticket_id = issue.get("key")
        updated = fields.get("updated")

        return {
            "id": ticket_id,
            "updated": updated,
            "content": f"Ticket: {ticket_id}\nSummary: {summary}\nDescription: {description}\n\nComments:\n{comments_text}"
        }

    def _extract_text_from_adf(self, adf):
        """Basic extractor for Atlassian Document Format."""
        if not adf or not isinstance(adf, dict):
            return str(adf)
        
        texts = []
        def walk(node):
            if isinstance(node, dict):
                if node.get("type") == "text":
                    texts.append(node.get("text", ""))
                for val in node.values():
                    walk(val)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        
        walk(adf)
        return " ".join(texts)
