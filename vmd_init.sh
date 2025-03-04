#!/bin/bash

echo "Initializing project structure..."

# Create necessary directories
mkdir -p docker_assets
mkdir -p volumes/input
mkdir -p volumes/index
mkdir -p volumes/models  # Add models directory

# Make all shell scripts executable
chmod +x vmd_*.sh

echo "Project structure initialized!"
echo "Place your markdown files in the ./volumes/input directory"
echo "Run ./vmd_build.sh to build the Docker image"
echo "Run ./vmd_start.sh to start the container"