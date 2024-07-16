# Muun Challenge: IP Blocklist microservice.

## Endpoint

### GET /check_ip/{ip}
- **Description**: Verify if an IP is on a blocklist.
- **Parameters**: 
  - `ip` (string): IP address to check.
- **Response**: 
  - `200 OK`: 
    - `{"blocked": true}`: If the IP is on the blocklist.
    - `{"blocked": false}`: If the IP is not on the blocklist.



## how to run 
docker-compose up --build


blocklist-updater-service
This is a separate service in order to perform updates from source of truth. The idea is it will run once every 24h or when starting up. 
Should not generate concurrency or downtime issues since it performs an update in a temporary key on redis and then switches to the key one used in `ip-checking-service`.