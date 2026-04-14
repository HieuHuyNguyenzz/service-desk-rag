import json
import os
import tempfile
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

    # Determine the sync start date
    sync_date_override = os.getenv("SYNC_DATE")
    if sync_date_override:
        # Ensure it's in a format Jira accepts (YYYY-MM-DD HH:mm)
        start_date = f"{sync_date_override} 00:00"
        print(f"Using SYNC_DATE override: {start_date}")
    else:
        start_date = state["last_sync"]
        print(f"Using last sync state: {start_date}")

    print(f"Fetching tickets for project {PROJECT_KEY} since {start_date}...")
    tickets = jira.get_tickets(PROJECT_KEY, updated_since=start_date)
    
    if not tickets:
        print("No new or updated tickets found.")
        return

    print(f"Found {len(tickets)} new or updated tickets from Jira API.")

    latest_updated = state["last_sync"]
    processed_count = 0
    skipped_count = 0

    for issue in tickets:
        ticket_data = jira.format_ticket(issue)
        ticket_id = ticket_data["id"]
        content = ticket_data["content"]
        summary = ticket_data["summary"]
        updated_time = ticket_data["updated"]

        # Only sync if ticket is new or has been updated
        last_known_update = state["mapping"].get(ticket_id)
        if last_known_update == updated_time:
            skipped_count += 1
            continue

        # Update last_sync tracker
        if not latest_updated or updated_time > latest_updated:
            latest_updated = updated_time

        try:
            print(f"Processing ticket {ticket_id} via Workflow...")
            
            # 1. Create a temporary file for the ticket content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                filename = f"{ticket_id}.txt"
                # 2. Upload to Dify
                file_id = dify.upload_file(tmp_path, filename)
                # 3. Run Workflow for LLM chunking/processing
                dify.run_workflow(filename, file_id)
                print(f"Successfully synced ticket {ticket_id} via workflow.")
                
                # Mark as synced in mapping
                state["mapping"][ticket_id] = updated_time
                processed_count += 1
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            print(f"Failed to sync ticket {ticket_id}: {e}")

    print(f"Sync Summary: Processed {processed_count}, Skipped {skipped_count}, Total {len(tickets)}")
    state["last_sync"] = latest_updated
    save_state(state)
    print("Sync completed successfully.")

if __name__ == "__main__":
    main()

