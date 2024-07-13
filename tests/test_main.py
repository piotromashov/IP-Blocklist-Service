import pytest
from fastapi.testclient import TestClient
from app.main import app, update_blocklist
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

def test_update_blocklist():
    # Simular la actualización del blocklist
    update_blocklist()
    # Verificar que las IPs se han actualizado correctamente
    assert redis_db.sismember("blocklist", "183.81.169.238")
    assert redis_db.sismember("blocklist", "194.169.175.36")
    assert not redis_db.sismember("blocklist", "8.8.8.8")

def test_blocklist_content():
    # Obtener las primeras 10 IPs del blocklist
    blocklist_ips = redis_db.smembers("blocklist")
    blocklist_ips_list = sorted(list(blocklist_ips))
    first_10_ips = blocklist_ips_list[:10]
    expected_ips = [
        "141.98.10.15",
        "143.92.49.143",
        "178.20.55.16",
        "183.81.169.238",
        "193.32.162.65",
        "193.32.162.83",
        "194.169.175.35",
        "194.169.175.36",
        "92.55.190.215",
        "93.174.95.106"
    ]
    assert first_10_ips == expected_ips
