# Service Desk RAG Sync

This project synchronizes tickets from Jira Service Management to Dify Knowledge for use in RAG (Retrieval-Augmented Generation) applications.

## Features
- Fetch tickets from Jira Service Management using REST API.
- Convert Atlassian Document Format (ADF) to plain text.
- Sync to Dify Knowledge dataset.
- Incremental synchronization using `sync_state.json` to avoid duplicates and update modified tickets.

## Setup

### 1. Configuration
Create a `.env` file in the root directory:
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=PROJ
DIFY_API_KEY=your-dify-api-key
DIFY_DATASET_ID=your-dify-dataset-id
DIFY_BASE_URL=https://your-dify-domain/v1
```

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Run
```bash
python main.py
```

## Deployment on Ubuntu Server (Daily Sync)

### 1. Environment Setup
```bash
sudo apt update
sudo apt install python3-venv python3-pip -y

git clone <your-repo-url>
cd service-desk-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Automation with systemd
Create a service file: `sudo nano /etc/systemd/system/service-desk-rag.service`
```ini
[Unit]
Description=Service Desk RAG Sync Service
After=network.target

[Service]
User=<your-username>
WorkingDirectory=/home/<your-username>/service-desk-rag
ExecStart=/home/<your-username>/service-desk-rag/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Create a timer file: `sudo nano /etc/systemd/system/service-desk-rag.timer`
```ini
[Unit]
Description=Run Service Desk RAG Sync daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 3. Activation
```bash
sudo systemctl daemon-reload
sudo systemctl enable service-desk-rag.timer
sudo systemctl start service-desk-rag.timer
```

### 4. Monitoring
Check logs:
```bash
journalctl -u service-desk-rag -f
```
Check timer status:
```bash
systemctl status service-desk-rag.timer
```
