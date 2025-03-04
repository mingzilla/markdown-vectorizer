#!/bin/bash

# Check if the parameter and value are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <parameter> <value>"
  echo "Example: $0 chunk_size 1000"
  echo "Example: $0 chunk_overlap 100"
  echo ""
  echo "Available parameters:"
  echo "  chunk_size     - Size of text chunks for vectorization"
  echo "  chunk_overlap  - Overlap between text chunks"
  exit 1
fi

PARAM="$1"
VALUE="$2"

# Convert parameter name to environment variable name
case "$PARAM" in
  chunk_size)
    ENV_VAR="CHUNK_SIZE"
    ;;
  chunk_overlap)
    ENV_VAR="CHUNK_OVERLAP"
    ;;
  *)
    echo "Unknown parameter: $PARAM"
    echo "Available parameters: chunk_size, chunk_overlap"
    exit 1
    ;;
esac

# Check if .env file exists, create if not
if [ ! -f .env ]; then
  echo "Creating .env file with default values..."
  echo "CHUNK_SIZE=512" > .env
  echo "CHUNK_OVERLAP=50" >> .env
fi

# Update .env file
if grep -q "^$ENV_VAR=" .env; then
  # Variable exists, update it
  sed -i "s/^$ENV_VAR=.*/$ENV_VAR=$VALUE/" .env
else
  # Variable doesn't exist, add it
  echo "$ENV_VAR=$VALUE" >> .env
fi

# Check if container is running
if docker ps | grep -q md-vectorizer; then
  echo "Updating running container..."
  # Update the environment variable in the running container
  docker exec md-vectorizer bash -c "export $ENV_VAR=$VALUE"
  echo "Note: Changes will fully apply when the container is restarted or when you run vectorization again."
fi

echo "$PARAM updated to $VALUE"
echo "The change will take effect the next time you run vectorization."
echo "Run ./vmd_process.sh to apply the new settings."