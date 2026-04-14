import json
import os
from datetime import datetime
from jira_client import JiraClient
from dify_client import DifyClient
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = "sync_state.json"

def load_state():
    default_state = {"last_sync": None, "mapping": {}}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                loaded_state = json.load(f)
                if isinstance(loaded_state, dict):
                    return {**default_state, **loaded_state}
        except (json.JSONDecodeError, IOError):
            pass
    return default_state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def main():
    # Configuration
    PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
    if not PROJECT_KEY:
        print("Error: JIRA_PROJECT_KEY not set in .env")
        return

    jira = JiraClient()
    dify = DifyClient()
    state = load_state()

    print(f"Fetching tickets for project {PROJECT_KEY}...")
    tickets = jira.get_tickets(PROJECT_KEY, updated_since=state["last_sync"])
    
    if not tickets:
        print("No new or updated tickets found.")
        return

    print(f"Found {len(tickets)} new or updated tickets.")

    latest_updated = state["last_sync"]

    for issue in tickets:
        ticket_data = jira.format_ticket(issue)
        ticket_id = ticket_data["id"]
        summary = ticket_data["summary"]
        content = ticket_data["content"]
        updated_time = ticket_data["updated"]
        
        # Update last_sync tracker
        if not latest_updated or updated_time > latest_updated:
            latest_updated = updated_time
        
        try:
            if ticket_id in state["mapping"]:
                # Update existing document
                doc_id = state["mapping"][ticket_id]
                print(f"Updating ticket {ticket_id} (Doc ID: {doc_id})...")
                dify.update_document(doc_id, content)
            else:
                # Create new document
                print(f"Creating document for ticket {ticket_id}...")
                result = dify.create_document(content, summary)
                doc_id = result.get("document", {}).get("id")
                state["mapping"][ticket_id] = doc_id
        except Exception as e:
            print(f"Failed to sync ticket {ticket_id}: {e}")


    state["last_sync"] = latest_updated
    save_state(state)
    print("Sync completed successfully.")

if __name__ == "__main__":
    main()
