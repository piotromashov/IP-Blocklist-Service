import redis
import os
from fastapi import FastAPI

app = FastAPI()

# Configuration for Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

@app.get("/check_ip/{ip}")
async def check_ip(ip: str):
    if redis_db.sismember("blocklist", ip):
        return {"blocked": True}
    return {"blocked": False}
