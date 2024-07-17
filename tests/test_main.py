import pytest
from fastapi.testclient import TestClient
from ipchecking.app.main import app
from blocklistupdater.app.main import update_blocklist
import redis
import os

# Configuración de Redis para pruebas
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_blocklist():
    # Configuración inicial del blocklist para pruebas
    redis_db.flushdb()  # Limpiar la base de datos de Redis
    sample_ips = [
        "183.81.169.238",
        "194.169.175.36",
        "194.169.175.35",
        "178.20.55.16",
        "93.174.95.106",
        "143.92.49.143",
        "193.32.162.65",
        "141.98.10.15",
        "92.55.190.215",
        "193.32.162.83"
    ]
    for ip in sample_ips:
        redis_db.sadd("blocklist", ip)
    yield
    redis_db.flushdb()  # Limpiar la base de datos de Redis después de las pruebas

def test_check_ip_blocked():
    response = client.get("/check_ip/183.81.169.238")
    assert response.status_code == 200
    assert response.json() == {"blocked": True}

def test_check_ip_not_blocked():
    response = client.get("/check_ip/8.8.8.8")
    assert response.status_code == 200
    assert response.json() == {"blocked": False}

