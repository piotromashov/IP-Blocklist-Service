import pytest
from unittest.mock import patch
import requests_mock
import tenacity
import redis
from blocklistupdater.app.main import update_blocklist, fetch_blocklist

# Sample blocklist data
sample_blocklist = """183.81.169.238
194.169.175.36
194.169.175.35
178.20.55.16
93.174.95.106
143.92.49.143
193.32.162.65
141.98.10.15
92.55.190.215
193.32.162.83
"""

large_blocklist = "\n".join([f"192.{k}.{j}.{i}" for i in range(256) for j in range(256) for k in range(17)])

allowed = [
    "8.8.8.8"
]

@pytest.fixture(scope="module")
def setup_redis():
    # Setup test Redis instance
    test_redis = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    yield test_redis
    test_redis.flushdb()  # Clean up after tests

def test_update_blocklist_success(setup_redis):
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", text=sample_blocklist)
        update_blocklist(redis_instance=setup_redis)
        blocklist = setup_redis.smembers("blocklist")
        assert "183.81.169.238" in blocklist
        assert "194.169.175.36" in blocklist
        assert len(blocklist) == 10

def test_fetch_blocklist_retry_logic(setup_redis):
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", status_code=500)
        with pytest.raises(tenacity.RetryError):
            fetch_blocklist()

def test_update_blocklist_redis_connection_error(setup_redis):
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", text=sample_blocklist)
        with pytest.raises(redis.exceptions.ConnectionError):
            with patch.object(setup_redis, 'pipeline', side_effect=redis.exceptions.ConnectionError):
                update_blocklist(redis_instance=setup_redis)

def test_update_blocklist_redis_timeout_error(setup_redis):
    with requests_mock.Mocker() as m:
        m.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", text=sample_blocklist)
        with pytest.raises(redis.exceptions.TimeoutError):
            with patch.object(setup_redis, 'pipeline', side_effect=redis.exceptions.TimeoutError):
                update_blocklist(redis_instance=setup_redis)
