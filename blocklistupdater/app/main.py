import redis
import requests
import time
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

BLOCKLIST_URL = "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"

# Define a retry strategy with exponential backoff
@retry(
    stop=stop_after_attempt(5),  # Stop after 5 attempts
    wait=wait_exponential(multiplier=1, min=4, max=60),  # Exponential backoff
    retry=retry_if_exception_type(requests.RequestException)  # Retry on requests exceptions
)
def fetch_blocklist():
    logger.info("Fetching blocklist...")
    response = requests.get(BLOCKLIST_URL)
    response.raise_for_status()
    return response.text.splitlines()

def update_blocklist():
    try:
        ips = fetch_blocklist()
        
        # Use a temporary key for the new blocklist
        temp_key = "blocklist_temp"
        
        # Start a Redis transaction
        pipeline = redis_db.pipeline()
        pipeline.multi()
        
        # Delete the temporary key if it exists
        pipeline.delete(temp_key)
        
        # Add the new IPs to the temporary key
        for ip in ips:
            pipeline.sadd(temp_key, ip.split()[0])
        
        # Atomically rename the temporary key to the blocklist key
        pipeline.rename(temp_key, "blocklist")
        
        # Execute the transaction
        pipeline.execute()
        
        logger.info("Blocklist updated successfully.")
    except requests.RequestException as e:
        logger.error(f"Error updating blocklist: {e}")

if __name__ == "__main__":
    while True:
        update_blocklist()
        time.sleep(86400)  # Update every 24 hours
