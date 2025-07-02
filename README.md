# Cloudflare DDNS Updater

This script automatically updates a Cloudflare DNS A record with your current public IP address, ensuring that your domain always points to the correct location. It fetches the public IP, compares it with the existing record, and updates it if a change is detected.

## Features

* Retrieves your public IP from multiple sources.
* Validates the IP format before proceeding.
* Updates Cloudflare DNS records using the Cloudflare API.
* Sends notifications via Slack, Discord, or email on success or failure.
* Designed to run as a scheduled cron job for automated updates.

## Requirements

* Python 3
* requests package (install with pip install requests)
* A Cloudflare account with an API key or token
* A .env file for storing credentials securely

## Setup
### 1. Install Dependencies

Ensure you have Python 3 and install the required package:
```shell
pip install requests
```
### 2. Create a .env File

Create a .env file in the same directory as the script and populate it with the necessary values:

```shell
AUTH_EMAIL="your-email@example.com"
AUTH_METHOD="global"  # or "token"
AUTH_KEY="your-cloudflare-api-key"
ZONE_IDENTIFIER="your-cloudflare-zone-id"
RECORD_NAME="your.domain.com"
TTL=120
PROXY=false
SITENAME="MyServer"
SLACKCHANNEL="#alerts"
SLACKURI="https://hooks.slack.com/services/your-slack-webhook"
DISCORDURI="https://discord.com/api/webhooks/your-discord-webhook"
EMAIL_HOST="smtp.example.com"
EMAIL_PORT=587
EMAIL_USERNAME="smtp-user"
EMAIL_PASSWORD="smtp-pass"
EMAIL_FROM="ddns@example.com"
EMAIL_TO="you@example.com"
```
### 3. Modify the Script to Load Environment Variables

Ensure the script reads from the .env file by adding this snippet at the beginning:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

auth_email = os.getenv("AUTH_EMAIL")
auth_method = os.getenv("AUTH_METHOD")
auth_key = os.getenv("AUTH_KEY")
zone_identifier = os.getenv("ZONE_IDENTIFIER")
record_name = os.getenv("RECORD_NAME")
ttl = int(os.getenv("TTL", 120))
proxy = os.getenv("PROXY").lower() == "true"
sitename = os.getenv("SITENAME")
slackchannel = os.getenv("SLACKCHANNEL")
slackuri = os.getenv("SLACKURI")
discorduri = os.getenv("DISCORDURI")
email_host = os.getenv("EMAIL_HOST")
email_port = int(os.getenv("EMAIL_PORT", "587"))
email_username = os.getenv("EMAIL_USERNAME")
email_password = os.getenv("EMAIL_PASSWORD")
email_from = os.getenv("EMAIL_FROM")
email_to = os.getenv("EMAIL_TO")
```
#### Note: Install python-dotenv if not already installed:
```shell
pip install python-dotenv
```
### 4. Test the Script

Run the script manually to ensure it works:
```shell
python3 ddns_updater.py
```

If the script runs successfully, it will update the Cloudflare record and send notifications if configured.

## Setting Up a Cron Job

To automate this script, use crontab:

1. Open the crontab editor:
```shell
crontab -e
```

2. Add the following line to run the script every 5 minutes:
```shell
*/5 * * * * /usr/bin/python3 /path/to/ddns_updater.py >> /var/log/ddns_updater.log 2>&1
```
3. Save and exit the crontab editor.

## Verify the Cron Job

To check if the cron job is running, use:
```shell
grep CRON /var/log/syslog
```

For questions or contributions, feel free to open an issue or submit a pull request!
