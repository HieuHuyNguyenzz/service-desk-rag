import requests
import os
from dotenv import load_dotenv

load_dotenv()

class JiraClient:
    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

    def get_tickets(self, project_key, updated_since=None):
        """
        Fetch tickets from a Jira project (On-premise/Data Center).
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
            }
            response = requests.get(f"{self.url}/rest/api/2/search", params=params, headers=self.headers)
            if response.status_code == 400:
                print(f"Jira API 400 Error Response: {response.text}")
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
        """Format ticket data into a string for Dify knowledge (On-premise)."""
        fields = issue.get("fields", {})
        summary = fields.get("summary", "No Summary")
        
        # Jira Server description is usually plain text or Wiki Markup string
        description = fields.get("description", "No Description")
        if not description:
            description = "No Description"

        # In Jira Server /rest/api/2/search with expand=comments, 
        # comments are available in fields['comment']['comments']
        comments_data = fields.get("comment", {}).get("comments", [])
        comments_text = "\n".join([c.get("body", "") for c in comments_data]) if comments_data else "No comments"
        
        ticket_id = issue.get("key")
        updated = fields.get("updated")

        return {
            "id": ticket_id,
            "updated": updated,
            "content": f"Ticket: {ticket_id}\nSummary: {summary}\nDescription: {description}\n\nComments:\n{comments_text}"
        }
