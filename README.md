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



## How to run locally
docker-compose up --build
go to [0.0.0.0:8000](http://0.0.0.0:8000)

## How to run tests
First have a redis instance running locally, you can do so using docker.
`docker run --name my-redis -d -p 6379:6379 redis:latest`
Then run 
`python tests/test_main.py`



## How to run with Kubernetes
chmod u+x setup_minikube.sh
./setup_minikube.sh
minikube service ipchecking --url

minikube dashboard

blocklistupdater-service
This is a separate service in order to perform updates on our local redis service from source of truth. This service will perform updates once every 24h or when starting up (whichever comes first, could be improved with a TTL flag to strictly perform updates every 24h).
Should not generate concurrency or downtime issues since it performs an update in a temporary key on redis and then switches the contentn to original key one used in `ipchecking-service`.
Has an exponential backoff retry mechanism on case of failure to get the endpoint data.


use separate services for checking IPs and updating the blocklist.
 This approach provides better scalability, fault isolation, and maintainability.



Future work for a production environment.
Generate metrics and a dashboard using Prometheus/Grafana to check the health and load of the services, and decide if there is need to scale or check for any issues.

Load testing, there are several services to try and perform stress tests, like Locust or k6.
Once the metrics are deployed and dashboards generated it would be nice to perform this stress tests and see real time how everything is working. 