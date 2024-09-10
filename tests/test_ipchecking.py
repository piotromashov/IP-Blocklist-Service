import pytest
from fastapi.testclient import TestClient
from ipchecking.app.main import app, redis_db
from blocklistupdater.app.main import update_blocklist
from tests.test_blocklistupdater import sample_blocklist, large_blocklist, allowed
import requests_mock
import redis
import time

client = TestClient(app)

## FIXTURES

@pytest.fixture(scope="module")
def setup_blocklist():
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", text=sample_blocklist)
        redis_db.flushdb()
        update_blocklist(redis_instance=redis_db)
        yield
        redis_db.flushdb()

@pytest.fixture(scope="module")
def setup_large_blocklist():
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", text=large_blocklist)
        redis_db.flushdb()
        update_blocklist(redis_instance=redis_db)
        yield
        redis_db.flushdb()

@pytest.fixture(scope="module")
def setup_corrupted_blocklist():
    redis_db.flushdb()  
    redis_db.set("blocklist", "not-a-set")
    yield
    redis_db.flushdb()  

## TESTS

def test_check_ip_blocked(setup_blocklist):
    blocklist = sample_blocklist.split()
    response = client.get("/check_ip/{first}".format(first=blocklist[0]))

    assert response.status_code == 200
    assert response.json() == {"blocked": True}

def test_check_ip_not_blocked(setup_blocklist):
    response = client.get("/check_ip/{allowed_ip}".format(allowed_ip=allowed[0]))

    assert response.status_code == 200
    assert response.json() == {"blocked": False}

def test_check_ip_invalid_format():
    response = client.get("/check_ip/invalid-ip")
    assert response.status_code == 422  # Unprocessable Entity

def test_check_ip_empty():
    response = client.get("/check_ip/")
    assert response.status_code == 404  # Not Found

def test_check_ip_large_blocklist(setup_large_blocklist):
    blocklist = large_blocklist.split()
    response = client.get("/check_ip/{last}".format(last=blocklist[len(blocklist) - 1]))
    assert response.status_code == 200
    assert response.json() == {"blocked": True}

def test_check_ip_not_in_large_blocklist(setup_large_blocklist):
    response = client.get("/check_ip/{allowed_ip}".format(allowed_ip=allowed[0]))
    assert response.status_code == 200
    assert response.json() == {"blocked": False}

def test_check_ip_performance(setup_large_blocklist):
    start_time = time.time()
    for _ in range(1000):
        response = client.get("/check_ip/192.16.255.255")
        assert response.status_code == 200
        assert response.json() == {"blocked": True}
    end_time = time.time()
    assert (end_time - start_time) < 10  # Ensure the test completes within 10 seconds

def test_check_ip_redis_connection_error(monkeypatch):
    def mock_redis_sismember(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Redis connection error")
    
    monkeypatch.setattr(redis_db, "sismember", mock_redis_sismember)
    
    response = client.get("/check_ip/183.81.169.238")
    assert response.status_code == 500  # Internal Server Error

def test_check_ip_redis_timeout_error(monkeypatch):
    def mock_redis_sismember(*args, **kwargs):
        raise redis.exceptions.TimeoutError("Redis timeout error")
    
    monkeypatch.setattr(redis_db, "sismember", mock_redis_sismember)
    
    response = client.get("/check_ip/183.81.169.238")
    assert response.status_code == 500  # Internal Server Error

def test_check_ip_redis_data_corruption(setup_corrupted_blocklist):
    response = client.get("/check_ip/183.81.169.238")
    assert response.status_code == 500  # Internal Server Error

