# Markdown Vectorizer

A simple Docker-based tool to convert markdown files into vector embeddings for semantic search.

## Project Structure

~~~
markdown-vectorizer/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
├── utils.py
├── vectorizer.py
├── api.py
├── vmd_build.sh
├── vmd_init.sh
├── vmd_process.sh
├── vmd_query.sh
├── vmd_start.sh
├── vmd_start_api.sh
└── volumes/
    ├── index/     # Where the vector database is stored
    └── input/     # Where you place your markdown files
~~~

## Get it from Docker Hub
~~~bash
docker pull mingzilla/md-vectorizer:v1.0
~~~


## Scripts

| Script             | Purpose                                     |
|--------------------|---------------------------------------------|
| `vmd_init.sh`      | Creates directories and sets permissions    |
| `vmd_build.sh`     | Builds the Docker image                     |
| `vmd_start.sh`     | Starts the container in the background      |
| `vmd_process.sh`   | Processes and vectorizes all markdown files |
| `vmd_query.sh`     | Queries the vector database                 |
| `vmd_start_api.sh` | Starts the API server for HTTP queries      |

## Getting Started

1. Download all files and run the initialization script:

~~~bash
./vmd_init.sh
~~~

2. Place your markdown files in the `volumes/input` directory

3. Build the Docker image:

~~~bash
./vmd_build.sh
~~~

4. Start the container:

~~~bash
./vmd_start.sh
~~~

5. Process your markdown files:

~~~bash
./vmd_process.sh
~~~

6. Query the vector database:

~~~bash
./vmd_query.sh "your search query" 5
~~~

The second parameter (5) is the number of results to return.

7. Start the API server (optional):

~~~bash
./vmd_start_api.sh
~~~

8. Query the vector database via API:

~~~bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"your search query", "num_results":5}'
~~~

## How It Works

This tool uses LlamaIndex with the following components:

- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Text Splitting**: Sentence-based chunking with 512 token chunks
- **Vector Database**: ChromaDB for storage and retrieval
- **Document Processing**: Simple markdown parsing
- **API**: Flask-based REST API for HTTP queries

When you run `vmd_process.sh`, all markdown files in the `volumes/input` directory are:

1. Read and parsed
2. Split into chunks
3. Converted to embeddings
4. Stored in the vector database

When you run `vmd_query.sh` or use the API:

1. Your query is converted to an embedding
2. Similar chunks are retrieved from the database
3. Results are displayed with their source files

## API Endpoints

The API server provides the following endpoints:

- **POST /api/query**: Query the vector database
  ```json
  {
    "query": "your search query",
    "num_results": 5
  }
  ```

- **GET /api/health**: Check if the API and vector database are healthy

## Customization

You can modify settings by editing the Python files:

- Change chunk size in `vectorizer.py` (default: 512 tokens)
- Change embedding model in `vectorizer.py` (default: all-MiniLM-L6-v2)
- Adjust the number of results when querying (default: 5)
