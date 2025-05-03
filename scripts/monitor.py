import asyncio
import aiohttp
import re
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import random
import socket
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CID = os.getenv("IMAGE_CID")
if not CID and __name__ == "__main__":
    raise ValueError("IMAGE_CID not found in .env")

# CID validation regex (IPFS v0: Qm..., v1: bafy...)
CID_PATTERN = re.compile(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{52})')

# User agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Get local IP to filter self-matches
local_ip = socket.gethostbyname(socket.gethostname())

async def fetch_page(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

async def monitor_cid(session, cid, logger_to_use=logger):
    url = f"https://www.google.com/search?q={cid}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    html = await fetch_page(session, url, headers)
    if not html:
        return {"status": "error", "message": f"Failed to fetch search results for CID {cid}"}

    soup = BeautifulSoup(html, "html.parser")
    results = []
    found = False
    for result in soup.select(".g, .yuRUbf"):
        link = result.select_one("a[href]")
        if not link or not link.get("href"):
            continue
        href = link["href"]
        parsed_url = urllib.parse.urlparse(href)
        query = urllib.parse.parse_qs(parsed_url.query)
        if "q" in query and cid in query["q"][0]:
            continue
        if local_ip in href or "localhost" in href or "127.0.0.1" in href or "google.com" in href:
            continue
        if cid in href:
            msg = f"Exact match found at: {href}"
            logger_to_use.info(msg)
            results.append(msg)
            found = True
        elif "ipfs" in href.lower() and CID_PATTERN.search(href):
            matched_cid = CID_PATTERN.search(href).group()
            if matched_cid != cid:
                msg = f"Possible IPFS match (CID: {matched_cid}) at: {href}"
                logger_to_use.info(msg)
                results.append(msg)
            else:
                msg = f"Exact IPFS match (CID: {matched_cid}) at: {href}"
                logger_to_use.info(msg)
                results.append(msg)
            found = True

    if not found:
        msg = "No matches found for CID."
        logger_to_use.info(msg)
        results.append(msg)
    return {"status": "success", "results": results}

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            logger.info(f"Monitoring CID: {CID}")
            await monitor_cid(session, CID)
            wait_time = random.uniform(60, 120)
            logger.info(f"Waiting {wait_time:.1f} seconds before next check...")
            await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")