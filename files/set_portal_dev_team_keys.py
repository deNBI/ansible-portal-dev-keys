#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

import requests

# Setup logging
logging.basicConfig(level=logging.INFO)

home = str(Path.home())
AUTHORIZED_KEYS = f"{home}/.ssh/authorized_keys"
OLD_AUTHORIZED_KEYS = f"{home}/.ssh/old.authorized_keys"
TEAM_MEMBERS_FILE = "/tmp/team_members.txt"

def get_team_members():
    logging.info("Getting Team Members")
    try:
        with open(TEAM_MEMBERS_FILE, 'r') as file:
            team_members = file.read().splitlines()
        logging.info(f"Found Team Members: {team_members}")
        return team_members
    except FileNotFoundError:
        logging.error(f"{TEAM_MEMBERS_FILE} not found!")
        sys.exit(1)

def check_for_errors(resp):
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"Request failed: {e}")
        logging.error(f"Content: {resp.content}")
        return False
    return True

def get_ssh_keys_user(user):
    logging.info(f"Getting SSH Keys for {user}")
    url = f"https://github.com/{user}.keys"
    response = requests.get(url)
    if check_for_errors(response):
        return response.text
    return ""

def read_existing_keys():
    if os.path.exists(AUTHORIZED_KEYS):
        with open(AUTHORIZED_KEYS, "r") as key_file:
            return {line.strip() for line in key_file if line.strip()}
    return set()

def write_keys_to_authorized_keys(keys, replace=False):
    # Write keys to authorized_keys file with an empty line after each key
    try:
        mode = "w" if replace else "a"
        with open(AUTHORIZED_KEYS, mode) as key_file:
            for key in keys.splitlines():
                key_file.write(f"{key}\n\n")
        if replace:
            logging.info("Keys successfully replaced in authorized keys!")
        else:
            logging.info("Keys successfully added to authorized keys!")
    except Exception as e:
        logging.error(f"Failed to write keys: {e}")

def remove_duplicates_from_authorized_keys():
    existing_keys = read_existing_keys()
    if existing_keys:
        try:
            with open(AUTHORIZED_KEYS, "w") as key_file:
                for key in existing_keys:
                    key_file.write(f"{key}\n\n")
            logging.info("Duplicates removed from authorized keys!")
        except Exception as e:
            logging.error(f"Failed to remove duplicates: {e}")

if __name__ == "__main__":
    replace = len(sys.argv) == 2 and sys.argv[1] == "-replace"

    if replace:
        if os.path.exists(AUTHORIZED_KEYS):
            os.rename(AUTHORIZED_KEYS, OLD_AUTHORIZED_KEYS)
            logging.info(f"Renamed {AUTHORIZED_KEYS} to {OLD_AUTHORIZED_KEYS}")

    remove_duplicates_from_authorized_keys()

    keys_to_add = ""
    existing_keys = read_existing_keys() if not replace else set()

    for member in get_team_members():
        user_keys = get_ssh_keys_user(member)
        if user_keys:
            for key in user_keys.split("\n"):
                key_entry = f"{key.strip()} {member}"
                if key and key_entry not in existing_keys:
                    keys_to_add += f"{key_entry}\n"

    if keys_to_add:
        write_keys_to_authorized_keys(keys_to_add, replace=replace)
    else:
        logging.info("No new keys to add.")
