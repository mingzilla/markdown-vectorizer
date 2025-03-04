#!/bin/bash

echo "Checking container status..."
docker ps -a | grep md-vectorizer

echo -e "\nContainer logs:"
docker logs md-vectorizer

echo -e "\nAttempting to execute a simple command in the container:"
docker exec -it md-vectorizer ls -la /app