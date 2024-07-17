#!/bin/bash

# Function to print messages
function print_message() {
  echo "=================================================="
  echo "$1"
  echo "=================================================="
}

print_message "Stopping and deleting existing Minikube cluster..."
minikube stop
minikube delete

# Start Minikube
print_message "Starting Minikube..."
minikube start --driver=docker

# Configure shell to use Minikube's Docker daemon
print_message "Configuring shell to use Minikube's Docker daemon..."
eval $(minikube -p minikube docker-env)

# Build Docker images
print_message "Building Docker images..."
docker build -t ipchecking:latest ./ipchecking
docker build -t blocklistupdater:latest ./blocklistupdater

# Apply Redis Configurations
print_message "Applying Redis configurations..."
kubectl apply -f kubernetes/redis-config.yaml
kubectl apply -f kubernetes/redis-statefulset.yaml
kubectl apply -f kubernetes/redis-service.yaml

# Apply IP Checking Service Configurations
print_message "Applying IP Checking Service configurations..."
kubectl apply -f kubernetes/ipchecking-deployment.yaml
kubectl apply -f kubernetes/ipchecking-service.yaml

# Apply Blocklist Updater Service Configurations
print_message "Applying Blocklist Updater Service configurations..."
kubectl apply -f kubernetes/blocklistupdater-deployment.yaml
kubectl apply -f kubernetes/blocklistupdater-service.yaml

# Wait for services to be ready
print_message "Waiting for services to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/ipchecking
kubectl wait --for=condition=available --timeout=600s deployment/blocklistupdater

echo "Done!"
