import os
import shutil
import hashlib
import logging
import json
import subprocess
from datetime import datetime, timedelta
import netrc
import requests
from base64 import b64encode

# -------------------------------------------------------
# Logging Setup
# -------------------------------------------------------
LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "upload.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Cleanup old logs
now = datetime.now()
for f in os.listdir(LOG_DIR):
    p = os.path.join(LOG_DIR, f)
    if os.path.isfile(p):
        if now - datetime.fromtimestamp(os.path.getmtime(p)) > timedelta(days=30):
            os.remove(p)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------------------------------------------
# Load Parameters
# -------------------------------------------------------
default_parameters = {
    "Repo Address": "https://cs-nexus.ukpn.local/repository/amp-generic",
    "Environment": ["Prod"],
    "DNO": ["EPN"],
    "Credentials": None,
    "tmp_folder": "/storage/amp/scripts/tmp",
    "backup_path": "/adms_backups/backups/oracle_backup_full_exclude_archive_admsstop_120420251900"
}

if os.path.exists(".env") and os.path.getsize(".env") > 0:
    try:
        parameters = json.load(open(".env"))
    except Exception:
        logging.warning(".env invalid JSON, using defaults.")
        parameters = default_parameters
else:
    parameters = default_parameters

# -------------------------------------------------------
# Cleanup Tmp Folder
# -------------------------------------------------------
tmp_dir = parameters["tmp_folder"]
if os.path.exists(tmp_dir):
    for item in os.listdir(tmp_dir):
        p = os.path.join(tmp_dir, item)
        try:
            if os.path.isfile(p) or os.path.islink(p):
                os.unlink(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
        except Exception as e:
            logging.warning("Failed to delete {}: {}".format(p, e))

# -------------------------------------------------------
# Load Nexus Credentials
# -------------------------------------------------------
netrc_path = "netrc-nexus"
try:
    auth = netrc.netrc(netrc_path)
    machine = "cs-nexus.ukpn.local"
    a = auth.authenticators(machine)
    if a:
        login, acct, password = a
        parameters["Credentials"] = {"username": login, "password": password}
    else:
        logging.error("No credentials found for {} in netrc".format(machine))
except Exception as e:
    logging.error("Failed to load netrc '{}': {}".format(netrc_path, e))

# -------------------------------------------------------
# Build Upload Path
# -------------------------------------------------------
repo_base = parameters["Repo Address"].rstrip("/")
env = parameters["Environment"][0]
dno = parameters["DNO"][0]
upload_dir = "{}/{}/{}".format(repo_base, env, dno)

# -------------------------------------------------------
# Nexus Connectivity Check (RAW repos return 404 normally)
# -------------------------------------------------------
def check_nexus(repo_url):
    try:
        cmd = [
            "curl", "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "--netrc-file", netrc_path,
            repo_url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        code = result.stdout.decode().strip()

        # RAW repositories return 404 for directories — this is normal
        if code in ("200", "404"):
            print("✅ Nexus repository reachable (HTTP {}).".format(code))
            logging.info("Nexus reachable (HTTP {}).".format(code))
        else:
            print("⚠️ Unexpected Nexus response: HTTP {}".format(code))
            logging.warning("Unexpected Nexus HTTP {}".format(code))

    except Exception as e:
        print("❌ Nexus connectivity error: {}".format(e))
        logging.error("Curl error: {}".format(e))

check_nexus(repo_base)

# -------------------------------------------------------
# SHA256 Calculation
# -------------------------------------------------------
def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

# -------------------------------------------------------
# File Upload via curl
# -------------------------------------------------------
def upload_to_nexus(local_path, url):
    try:
        cmd = [
            "curl",
            "--netrc-file", netrc_path,
            "-T", local_path,
            url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout = result.stdout.decode().strip()
        stderr = result.stderr.decode().strip()

        logging.info("Upload stdout: {}".format(stdout))
        if stderr:
            logging.warning("Upload stderr: {}".format(stderr))

        # Nexus returns 201 Created or 200 OK
        if "201" in stdout or "200" in stdout:
            print("✅ Upload successful: {}".format(url))
            logging.info("Upload success: {}".format(url))
        else:
            print("⚠️ Upload may have failed (check log): {}".format(stdout))
            logging.warning("Possible upload failure: {}".format(stdout))

    except Exception as e:
        print("❌ Upload error: {}".format(e))
        logging.error("Upload exception: {}".format(e))

# -------------------------------------------------------
# Upload Backup Files
# -------------------------------------------------------
backup_path = parameters["backup_path"]


