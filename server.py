from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from main import process_image, revoke_access
import asyncio
import aiohttp
import re
from scripts.monitor import monitor_cid, CID_PATTERN
from scripts.revoke_access import verify_revocation  # Import verify_revocation

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

# Configure Flask logger to match the format of main.py
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# Load environment variables for verify_revocation
from dotenv import load_dotenv
load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

@app.route("/api/protect", methods=["POST"])
def protect_image():
    app.logger.info(f"Received request to /api/protect with form data: {request.form}, files: {list(request.files.keys())}")

    if "image" not in request.files:
        app.logger.error("No image uploaded in request")
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    is_public = request.form.get("isPublic", "false").lower() == "true"
    secret = request.form.get("secret", None)

    app.logger.info(f"Processing image: {file.filename}, isPublic: {is_public}, secret: {secret if secret else 'default from env'}")

    os.makedirs("data/clean", exist_ok=True)
    clean_path = os.path.join("data/clean", file.filename)
    file.save(clean_path)
    app.logger.info(f"Saved uploaded image to {clean_path}")

    try:
        result = process_image(clean_path, is_public, secret=secret)
        app.logger.info(f"Image processing successful, returning result: {result}")
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error during image processing: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(clean_path):
            os.remove(clean_path)
            app.logger.info(f"Cleaned up temporary file: {clean_path}")

@app.route("/api/revoke", methods=["POST"])
def revoke():
    app.logger.info(f"Received request to /api/revoke with data: {request.get_json()}")

    data = request.get_json()
    cid = data.get("cid") if data else None
    if not cid:
        app.logger.error("CID is required but not provided")
        return jsonify({"error": "CID is required"}), 400

    app.logger.info(f"Checking revocation status for CID: {cid}")
    try:
        # Check if the CID is already revoked
        is_revoked = verify_revocation(SEPOLIA_RPC_URL, CONTRACT_ADDRESS, cid)
        if is_revoked:
            app.logger.info(f"CID {cid} is already revoked")
            return jsonify({"success": True, "message": "CID is already revoked"}), 200
    except Exception as e:
        app.logger.error(f"Error checking revocation status for CID {cid}: {str(e)}")
        # Proceed with revocation even if verification fails, to avoid blocking the process

    app.logger.info(f"Revoking access for CID: {cid}")
    try:
        revoke_access(cid)
        app.logger.info(f"Access revoked successfully for CID: {cid}")
        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error during revocation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/monitor", methods=["POST"])
def monitor():
    app.logger.info(f"Received request to /api/monitor with data: {request.get_json()}")

    data = request.get_json()
    cid = data.get("cid") if data else None
    if not cid:
        app.logger.error("CID is required but not provided")
        return jsonify({"error": "CID is required"}), 400

    if not CID_PATTERN.match(cid):
        app.logger.error(f"Invalid CID format: {cid}")
        return jsonify({"error": "Invalid CID format"}), 400

    app.logger.info(f"Monitoring CID: {cid}")
    try:
        # Define the async function to run
        async def run_monitor():
            async with aiohttp.ClientSession() as session:
                return await monitor_cid(session, cid, logger_to_use=app.logger)

        # Use asyncio.run to create a new event loop for this request
        result = asyncio.run(run_monitor())
        app.logger.info(f"Monitoring completed for CID {cid}, result: {result}")
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error during monitoring: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.logger.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)