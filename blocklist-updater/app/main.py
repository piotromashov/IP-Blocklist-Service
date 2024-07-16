# blocklist-updater-service/app/main.py
import redis
import requests
import time
from fastapi import FastAPI

app = FastAPI()

# Configuration for Redis
redis_host = 'redis'
redis_port = 6379
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

BLOCKLIST_URL = "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"

def update_blocklist():
    try:
        response = requests.get(BLOCKLIST_URL)
        response.raise_for_status()
        ips = response.text.splitlines()
        
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
        
        print("Blocklist updated successfully.")
    except requests.RequestException as e:
        print(f"Error updating blocklist: {e}")

@app.on_event("startup")
async def startup_event():
    while True:
        update_blocklist()
        time.sleep(86400)  # Update every 24 hours
