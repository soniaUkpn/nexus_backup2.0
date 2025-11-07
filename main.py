import os
import shutil
import hashlib
import logging
from datetime import datetime, timedelta
import subprocess
import requests
from base64 import b64encode
import json

# Setup logging
LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "upload.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Remove logs older than 30 days
now = datetime.now()
for log_file in os.listdir(LOG_DIR):
    file_path = os.path.join(LOG_DIR, log_file)
    if os.path.isfile(file_path):
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_time > timedelta(days=30):
            os.remove(file_path)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Clean up tmp folder
TMP_FOLDER = "/storage/amp/scripts/tmp"
if os.path.exists(TMP_FOLDER):
    for filename in os.listdir(TMP_FOLDER):
        file_path = os.path.join(TMP_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.warning(f"Failed to delete {file_path}. Reason: {e}")

# Load parameters

default_parameters = {
    "Repo Address": "https://cs-nexus.ukpn.local/repository/amp-generic/",
    "Environment": ["Prod"],
    "DNO": ["EPN"],
    "Credentials": None,
    "tmp_folder": "/storage/amp/scripts/tmp",
    "backup_path": "/adms_backups/backups/oracle_backup_full_exclude_archive_admsstop_120420251900"
}

if os.path.exists(".env") and os.path.getsize(".env") > 0:
    try:
        with open(".env", "r") as f:
            parameters = json.load(f)
    except json.JSONDecodeError:
        logging.warning(".env file is not valid JSON. Falling back to default parameters.")
        parameters = default_parameters
else:
    parameters = default_parameters


# Load credentials from netrc-nexus file
try:
    netrc_path = "netrc-nexus"
    auth_data = netrc.netrc(netrc_path)
    machine = "cs-nexus.ukpn.local"
    login, account, password = auth_data.authenticators(machine)
    parameters["Credentials"] = {
        "username": login,
        "password": password
    }
except (FileNotFoundError, netrc.NetrcParseError, TypeError) as e:
    logging.error(f"Failed to load credentials from {netrc_path}: {e}")


# Construct repository path
#environment = parameters["Environment"][0]
#dno = parameters["DNO"][0]
#repository = f"backups/{environment}/{dno}"
#nexus_url = parameters["Repo Address"].rstrip("/")
