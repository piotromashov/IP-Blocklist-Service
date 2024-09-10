import redis
import os
import logging
from fastapi import FastAPI, HTTPException
from ipaddress import IPv4Address, AddressValueError

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)


@app.get("/check_ip/{ip}")
async def check_ip(ip: str):
    try:
        # Validate IP format
        IPv4Address(ip)
        
        # Check if IP is in blocklist
        if redis_db.sismember("blocklist", ip):
            return {"blocked": True}
        return {"blocked": False}
    except AddressValueError as e:
        raise HTTPException(status_code=422, detail="Invalid IP address format")
    except redis.exceptions.ConnectionError:
        logger.error("Redis connection error")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except redis.exceptions.TimeoutError:
        logger.error("Redis timeout error")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/check_ip/")
async def check_ip_empty():
    raise HTTPException(status_code=404, detail="IP address is required")
