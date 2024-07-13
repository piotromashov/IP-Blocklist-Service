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