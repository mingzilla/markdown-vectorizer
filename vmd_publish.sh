#!/bin/bash

docker login
docker tag tool-markdown-vectorizer-md-vectorizer mingzilla/md-vectorizer:v1.0
docker push mingzilla/md-vectorizer:v1.0

# to pull, use
# docker pull mingzilla/md-vectorizer:v1.0