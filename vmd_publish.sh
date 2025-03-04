#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible."
  exit 1
fi

# Check if image exists
if ! docker images | grep -q "md-vectorizer"; then
  echo "Error: md-vectorizer image not found."
  echo "Build it first with: ./vmd_build.sh"
  exit 1
fi

echo "Publishing md-vectorizer to Docker Hub..."

# Tag the image
docker tag md-vectorizer mingzilla/md-vectorizer:v1.2

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username"; then
  echo "You need to log in to Docker Hub first."
  echo "Run: docker login"
  exit 1
fi

# Push to Docker Hub
echo "Pushing to Docker Hub as mingzilla/md-vectorizer:v1.2..."
docker push mingzilla/md-vectorizer:v1.2

echo "Publication complete!"
echo "Image is now available at: mingzilla/md-vectorizer:v1.2"