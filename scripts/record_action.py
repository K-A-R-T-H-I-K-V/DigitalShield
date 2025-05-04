import os
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path for the record file (local path)
RECORD_FILE = "data/revocation_log.json"

def record_action(cid, action, details=""):
    """
    Record an action (e.g., revocation) with a timestamp.
    Args:
        cid (str): The CID of the asset.
        action (str): The action taken (e.g., "revoked").
        details (str): Additional details about the action.
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "cid": cid,
        "action": action,
        "details": details
    }

    # Load existing records or initialize an empty list
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, "r") as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError):
            records = []
    else:
        records = []

    # Append the new record
    records.append(log_entry)

    # Save the updated records
    try:
        with open(RECORD_FILE, "w") as f:
            json.dump(records, f, indent=4)
        logger.info(f"Recorded action: {action} for CID {cid} at {timestamp}")
    except IOError as e:
        logger.error(f"Failed to write to record file: {e}")

if __name__ == "__main__":
    # Test the recording
    record_action("test-cid", "test-action", "This is a test.")