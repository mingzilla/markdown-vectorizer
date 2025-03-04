#!/bin/bash

echo "Starting API server in the container..."

# Wait for container to be ready
MAX_ATTEMPTS=30
ATTEMPT=0
CONTAINER_READY=false

echo "Waiting for container to be ready..."
while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ "$CONTAINER_READY" = false ]; do
  CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' md-vectorizer 2>/dev/null)

  if [ "$CONTAINER_STATUS" = "running" ]; then
    CONTAINER_READY=true
    echo "Container is ready!"
  else
    ATTEMPT=$((ATTEMPT+1))
    echo "Container not ready yet. Waiting... (Attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  fi
done

if [ "$CONTAINER_READY" = false ]; then
  echo "Error: Container failed to start within the expected time."
  echo "Check the container logs with: docker logs md-vectorizer"
  exit 1
fi

# Stop any previously running Flask app
docker exec md-vectorizer pkill -f "flask run" || true

# Start Flask app in the foreground with proper output
docker exec -it md-vectorizer bash -c "cd /app && export FLASK_APP=api.py && flask run --host=0.0.0.0 --port=5000"

echo "API server started on http://localhost:5000"
echo "Try the health check at: http://localhost:5000/api/health"
echo "You can query the vector database with:"
echo "curl -X POST http://localhost:5000/api/query -H 'Content-Type: application/json' -d '{\"query\":\"your query text\",\"num_results\":5}'"