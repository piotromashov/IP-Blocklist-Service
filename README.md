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

## Requirements
Python, Docker, Minikube, Unix.

## How to run locally
1. Execute `docker-compose up --build`   
2. Then go to [0.0.0.0:8000](http://0.0.0.0:8000)

## How to run tests
1. First have a redis instance running locally, you can do so using docker.  
`docker run --name my-redis -d -p 6379:6379 redis:latest`  
2. Install all needed requirements.  
`pip install -r blocklistupdater/requirements.txt`  
`pip install -r ipchecking/requirements.txt`  
`pip install -r tests/requirements.txt`  
3. Then run: 
`python tests/test_main.py`

## How to run with Kubernetes

1. Give execution permisions to `setup_minikube.sh`:   
`chmod u+x setup_minikube.sh`
2. Then run `./setup_minikube.sh`.  
3. Once the process is done, you can check the service via  
`minikube service ipchecking --url`
4. You can also checkout the dashboard to enter the pods and see their logs  
`minikube dashboard`



## Summary 
We use separated services for checking IPs and updating the blocklist locally.
We want to avoid making external calls for each call to our service, thus we save the blocklist locally in redis in memory. This gives us a faster response and avoids any latency and downtime that our external connections could have.

Our approach ensures operational stability and performance under heavy load through the following key strategies:

- **Redis Master-Replica Configuration:** Provides high availability, fault tolerance, and scalability for read and write operations.
- **Dedicated Blocklist Updater Service:** Ensures efficient and reliable updates to the blocklist without affecting the IP checking service.
- **High-Performance IP Checking Service:** Built using FastAPI for low latency and high concurrency, with the ability to scale horizontally.
- **Kubernetes Orchestration:** Automates the management, scaling, and monitoring of the services, ensuring that they remain operational and responsive under varying loads.


### Ip Checking
The IP checking service is built using FastAPI, which is known for its high performance and low latency. FastAPI leverages asynchronous programming to handle a large number of concurrent requests efficiently.   
This is the main service exposing the endpoint /check_ip/

#### Features:
* Horizontal Scaling: The IP checking service can be horizontally scaled by increasing the number of replicas. Kubernetes can automatically distribute the load across multiple instances, ensuring that the service remains responsive under heavy load.


### Blocklist Updater
This is a separate service in order to perform updates on our local redis service from source of truth. This service will perform updates once every 24h or when starting up (whichever comes first, could be improved with a TTL flag to strictly perform updates every 24h). 

#### Features:

* Separation of Concerns: By separating the blocklist update functionality into a dedicated service, we ensure that the IP checking service is not affected by the update process. This separation allows each service to be optimized for its specific workload. 

* Exponential Backoff: The blocklist updater service uses an exponential backoff strategy for retries, ensuring that temporary network issues do not overwhelm the system with repeated requests.

* Atomic Updates: By using a temporary key and renaming it atomically, we ensure that the blocklist is updated in a consistent and atomic manner, preventing partial updates and ensuring data integrity. 


### Redis
Redis is an in-memory data store, providing extremely low latency for both read and write operations. This ensures that the system can respond quickly even under heavy load.

#### Features
* By using a master-replica setup, we ensure that the data is replicated across multiple nodes. If the master node fails, the replicas can still serve read requests, and a new master can be promoted to handle write operations.

### Kubernetes
Kubernetes Deployments manage redis, blocklist updater and the IP checking services, ensuring that they are always running the desired number of replicas. Kubernetes can automatically restart failed pods and distribute the load across the cluster, ensuring high availability and operational under heavy load.



## Future work for a production environment.
1. Generate metrics and a dashboard using Prometheus/Grafana to check the health and load of the services, and decide if there is need to scale or check for any issues.
2. Load testing, there are several services to try and perform stress tests, like Locust or k6.
3. Implement Redis Sentinel, we can automatically detect failures and promote a replica to master, ensuring minimal downtime.