from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import redis
import os
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager

app = FastAPI()

# Redis configuration
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# Public URL of blocked IPs
BLOCKLIST_URL = "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On app startup
    await update_blocklist()
    yield
    # On app shutdown
    print("Application shutdown")

app.router.lifespan_context = lifespan

@repeat_every(seconds=24*60*60)  # Execute every 24h
async def periodic_update():
    await update_blocklist()


async def update_blocklist():
    print("Updating blocklist...")
    try:
        response = requests.get(BLOCKLIST_URL)
        response.raise_for_status()
        lines = response.text.splitlines()
        ips = [line.split()[0] for line in lines]  # only save the IPs
        redis_db.delete("blocklist")
        for ip in ips:
            redis_db.sadd("blocklist", ip)
        print("Blocklist updated successfully.")
    except requests.RequestException as e:
        print(f"Error updating blocklist: {e}")

@app.get("/check_ip/{ip}")
async def check_ip(ip: str):
    if redis_db.sismember("blocklist", ip):
        return {"blocked": True}
    return {"blocked": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
