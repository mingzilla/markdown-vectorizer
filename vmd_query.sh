#!/bin/bash

# Check if query text is provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <query_text> [num_results]"
  echo "Example: $0 \"What is a vector database?\" 5"
  exit 1
fi

# Get query parameters
QUERY_TEXT="$1"
NUM_RESULTS="${2:-5}"  # Default to 5 results if not specified

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

# Execute query inside the container
docker exec md-vectorizer python vectorizer.py query "$QUERY_TEXT" "$NUM_RESULTS"