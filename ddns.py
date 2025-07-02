#!/usr/bin/python3
import requests
import re
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get values from environment variables
auth_email = os.getenv("AUTH_EMAIL")
auth_method = os.getenv("AUTH_METHOD")
auth_key = os.getenv("AUTH_KEY")
zone_identifier = os.getenv("ZONE_IDENTIFIER")
record_name = os.getenv("RECORD_NAME")
ttl = int(os.getenv("TTL", 120))  # Default to 120 if not set
proxy = os.getenv("PROXY", "False").lower() == "true"  # Convert to boolean
sitename = os.getenv("SITENAME")
slackchannel = os.getenv("SLACKCHANNEL")
slackuri = os.getenv("SLACKURI")
discorduri = os.getenv("DISCORDURI")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Get public IP
def get_public_ip():
    try:
        ip_info = requests.get('https://cloudflare.com/cdn-cgi/trace').text
        ip = re.search(r'^ip=([0-9.]+)$', ip_info, re.MULTILINE).group(1)
    except:
        try:
            ip = requests.get('https://myexternalip.com/raw').text.strip()
        except:
            ip = requests.get('https://ipv4.icanhazip.com').text.strip()
    return ip

# Validate IP
def validate_ip(ip):
    ipv4_regex = re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$')
    return ipv4_regex.match(ip) is not None

ip = get_public_ip()
if not validate_ip(ip):
    logging.error("DDNS Updater: Failed to find a valid IP.")
    exit(2)

# Set the proper auth header
if auth_method == "global":
    auth_header = {"X-Auth-Key": auth_key}
else:
    auth_header = {"Authorization": f"Bearer {auth_key}"}

# Seek for the A record
record_response = requests.get(
    f"https://api.cloudflare.com/client/v4/zones/{zone_identifier}/dns_records",
    headers={
        "X-Auth-Email": auth_email,
        "Content-Type": "application/json",
        **auth_header
    },
    params={"type": "A", "name": record_name}
).json()

# Check if the domain has an A record
if record_response['result_info']['count'] == 0:
    logging.error(f"DDNS Updater: Record does not exist, perhaps create one first? ({ip} for {record_name})")
    exit(1)

# Get existing IP
old_ip = record_response['result'][0]['content']

# Compare if they're the same
if ip == old_ip:
    logging.info(f"DDNS Updater: IP ({ip}) for {record_name} has not changed.")
    exit(0)
else:
    # Set the record identifier from result
    record_identifier = record_response['result'][0]['id']

    # Change the IP at Cloudflare using the API
    update_response = requests.patch(
        f"https://api.cloudflare.com/client/v4/zones/{zone_identifier}/dns_records/{record_identifier}",
        headers={
            "X-Auth-Email": auth_email,
            "Content-Type": "application/json",
            **auth_header
        },
        data=json.dumps({
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": ttl,
            "proxied": proxy
        })
    ).json()

    # Report the status
    if not update_response['success']:
        logging.error(f"DDNS Updater: {ip} {record_name} DDNS failed for {record_identifier} ({ip}). DUMPING RESULTS:\n{update_response}")
        if slackuri:
            requests.post(slackuri, json={
                "channel": slackchannel,
                "text": f"{sitename} DDNS Update Failed: {record_name}: {record_identifier} ({ip})."
            })
        if discorduri:
            requests.post(discorduri, json={
                "content": f"{sitename} DDNS Update Failed: {record_name}: {record_identifier} ({ip})."
            })
        exit(1)
    else:
        logging.info(f"DDNS Updater: {ip} {record_name} DDNS updated.")
        if slackuri:
            requests.post(slackuri, json={
                "channel": slackchannel,
                "text": f"{sitename} Updated: {record_name}'s new IP Address is {ip}"
            })
        if discorduri:
            requests.post(discorduri, json={
                "content": f"{sitename} Updated: {record_name}'s new IP Address is {ip}"
            })
        exit(0)
