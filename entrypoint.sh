#!/bin/bash
set -e

echo "Container starting..."
echo "Setting environment variable for Flask..."
export FLASK_APP=api.py

# Run a test to ensure all imports work
echo "Testing imports..."
python -c "
try:
    from llama_index import Document, VectorStoreIndex, StorageContext
    from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
    from llama_index.vector_stores import ChromaVectorStore
    from llama_index.embeddings.langchain import LangchainEmbedding
    from langchain.embeddings import HuggingFaceEmbeddings
    import chromadb
    print('All imports successful!')
except Exception as e:
    print(f'Import error: {str(e)}')
    print('Continuing anyway...')
"

# Install additional system tools that might be useful
echo "Installing additional tools..."
apt-get update && apt-get install -y procps

# Start Flask app in the background
echo "Starting Flask API in the background..."
cd /app
python -m flask run --host=0.0.0.0 --port=5000 &

# Keep container running
echo "Starting infinite loop to keep container running"
while true; do
  sleep 60 &
  wait $!
done