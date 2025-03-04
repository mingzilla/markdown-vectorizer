import os
import json
import logging
from typing import Dict, Any, Optional, List

from flask import Flask, request, jsonify
from vectorizer import MarkdownVectorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("md-vectorizer-api")

# Initialize Flask app
app = Flask(__name__)

# Set up constants
INDEX_DIR = "/volumes/index"


class VectorDBAPI:
    """API class for vector database operations."""

    @staticmethod
    def query_vector_db(query_text: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector database.

        Args:
            query_text: The query text
            num_results: Number of results to return

        Returns:
            List of results
        """
        logger.info(f"Querying vector DB with: '{query_text}', num_results={num_results}")

        try:
            results = MarkdownVectorizer.query_index(query_text, INDEX_DIR, num_results)
            return results
        except Exception as e:
            logger.error(f"Error querying vector DB: {str(e)}")
            return []


@app.route('/api/query', methods=['POST'])
def query_endpoint() -> Dict[str, Any]:
    """
    API endpoint to query the vector database.

    Expects a JSON body with:
    {
        "query": "your query text",
        "num_results": 5  (optional, defaults to 5)
    }

    Returns:
        JSON response with query results
    """
    try:
        # Get request data
        data = request.json

        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required parameter: query'
            }), 400

        query_text = data['query']
        num_results = int(data.get('num_results', 5))

        # Query vector DB
        results = VectorDBAPI.query_vector_db(query_text, num_results)

        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'score': result['score'],
                'content': result['content'],
                'source': result['metadata'].get('source', 'Unknown'),
                'metadata': result['metadata']
            })

        return jsonify({
            'query': query_text,
            'num_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        JSON response with status
    """
    try:
        # Check if index directory exists and has files
        index_exists = os.path.exists(INDEX_DIR) and os.listdir(INDEX_DIR)

        return jsonify({
            'status': 'healthy',
            'index_available': bool(index_exists)
        })

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def root() -> Dict[str, Any]:
    """
    Root endpoint for basic testing.

    Returns:
        Simple welcome message
    """
    return jsonify({
        'message': 'Markdown Vectorizer API is running',
        'usage': {
            'query': 'POST /api/query with JSON body {"query": "your search query", "num_results": 5}',
            'health': 'GET /api/health'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)