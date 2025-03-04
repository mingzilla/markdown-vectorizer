#!/bin/bash

echo "Starting md-vectorizer container..."
docker-compose up -d

echo "Container started in background!"
echo "Place your markdown files in the ./volumes/input directory"
echo "Then run ./vmd_process.sh to vectorize them"
