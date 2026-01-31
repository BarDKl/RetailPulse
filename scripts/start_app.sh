#!/bin/bash

# Build and start the containers in detached mode
echo "Starting RetailPulse services..."
docker-compose up -d --build

echo "Waiting for services to initialize..."
sleep 10

echo "Services should be running!"
echo "Airflow UI: http://localhost:8080"
echo "Retail API Docs: http://localhost:8000/docs"
