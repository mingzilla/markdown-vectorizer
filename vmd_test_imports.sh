#!/bin/bash

echo "Testing imports in the container..."
docker exec md-vectorizer python -c "
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
"