import os
import sys
import logging
from typing import List, Dict, Any, Optional

from llama_index import Document, VectorStoreIndex, StorageContext, ServiceContext
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.vector_stores import ChromaVectorStore
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings import HuggingFaceEmbeddings
import chromadb

from utils import FileUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("md-vectorizer")


class MarkdownVectorizer:
    """Main class to handle vectorization of markdown files."""

    @staticmethod
    def setup_embedding_model():
        """
        Set up the embedding model.

        Returns:
            The embedding model
        """
        # Configure cache directory for models
        model_cache_dir = "/volumes/models"
        os.makedirs(model_cache_dir, exist_ok=True)

        # Use lightweight all-MiniLM-L6-v2 model (384 dimensions)
        hf_embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder=model_cache_dir
        )
        embed_model = LangchainEmbedding(hf_embeddings)
        logger.info(f"Embedding model set up with cache dir: {model_cache_dir}")
        return embed_model

    @staticmethod
    def setup_service_context(embed_model):
        """
        Set up ServiceContext with only embedding model and no LLM.

        Args:
            embed_model: The embedding model

        Returns:
            ServiceContext without LLM dependency
        """
        # Create ServiceContext with embed_model but no llm
        # In llama-index 0.8.4, we use llm=None to avoid LLM initialization
        service_context = ServiceContext.from_defaults(
            embed_model=embed_model,
            llm=None
        )
        return service_context

    @staticmethod
    def setup_chroma_db(persist_dir: str) -> chromadb.PersistentClient:
        """
        Set up ChromaDB client.

        Args:
            persist_dir: Directory where ChromaDB will store data

        Returns:
            A ChromaDB client
        """
        os.makedirs(persist_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=persist_dir)
        logger.info(f"ChromaDB initialized at {persist_dir}")
        return client

    @staticmethod
    def process_markdown_files(input_dir: str, index_dir: str) -> None:
        """
        Process all markdown files in the input directory and add them to the vector store.

        Args:
            input_dir: Directory containing markdown files
            index_dir: Directory where the vector store will be saved

        Returns:
            None
        """
        logger.info(f"Starting to process markdown files from {input_dir}")

        # Set up embedding model
        embed_model = MarkdownVectorizer.setup_embedding_model()

        # Set up service context with no LLM
        service_context = MarkdownVectorizer.setup_service_context(embed_model)

        # Get list of markdown files
        markdown_files = FileUtils.get_markdown_files(input_dir)
        if not markdown_files:
            logger.warning(f"No markdown files found in {input_dir}")
            return

        logger.info(f"Found {len(markdown_files)} markdown files")

        # Process each file
        documents = []
        for file_path in markdown_files:
            try:
                text, metadata = FileUtils.read_markdown_file(file_path)
                doc = Document(text=text, metadata=metadata)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")

        # Set up ChromaDB
        client = MarkdownVectorizer.setup_chroma_db(index_dir)
        chroma_collection = client.get_or_create_collection("markdown_docs")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Define text splitter for chunking
        text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)

        # Create vector store index - use service_context to avoid LLM initialization
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            service_context=service_context,
            text_splitter=text_splitter,  # In 0.8.4, pass text_splitter separately
            show_progress=True
        )

        logger.info(f"Vectorization complete. Documents indexed: {len(documents)}")

    @staticmethod
    def query_index(query_text: str, index_dir: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector index for relevant documents.

        Args:
            query_text: The query text
            index_dir: Directory where the vector store is saved
            num_results: Number of results to return

        Returns:
            List of dictionaries containing relevant document info
        """
        try:
            # Set up embedding model
            embed_model = MarkdownVectorizer.setup_embedding_model()

            # Set up service context with no LLM
            service_context = MarkdownVectorizer.setup_service_context(embed_model)

            # Set up ChromaDB
            client = MarkdownVectorizer.setup_chroma_db(index_dir)
            chroma_collection = client.get_or_create_collection("markdown_docs")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # Create index with our service context (no LLM)
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                service_context=service_context
            )

            # Create retriever
            retriever = index.as_retriever(similarity_top_k=num_results)

            # Query
            results = retriever.retrieve(query_text)

            # Format results
            output = []
            for result in results:
                content = None
                # Handle different versions of llama-index and their result objects
                if hasattr(result, 'node') and hasattr(result.node, 'get_content'):
                    content = result.node.get_content()
                    metadata = result.node.metadata if hasattr(result.node, 'metadata') else {}
                elif hasattr(result, 'source_node') and hasattr(result.source_node, 'get_content'):
                    content = result.source_node.get_content()
                    metadata = result.source_node.metadata if hasattr(result.source_node, 'metadata') else {}
                elif hasattr(result, 'text'):
                    content = result.text
                    metadata = result.metadata if hasattr(result, 'metadata') else {}
                else:
                    # Last resort - try to get content directly as a string or repr
                    try:
                        content = str(result)
                    except:
                        content = "Content could not be extracted"
                    metadata = {}

                output.append({
                    "score": result.score,
                    "content": content,
                    "metadata": metadata
                })

            return output

        except Exception as e:
            logger.error(f"Error querying index: {str(e)}")
            raise  # Re-raise to see full traceback

if __name__ == "__main__":
    """
    Command-line interface for processing markdown files or querying the index.

    Usage:
        # Process markdown files
        python vectorizer.py process

        # Query the index
        python vectorizer.py query "your query text" [num_results]
    """
    input_dir = "/volumes/input"
    index_dir = "/volumes/index"

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python vectorizer.py process")
        print("  python vectorizer.py query \"your query text\" [num_results]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "process":
        MarkdownVectorizer.process_markdown_files(input_dir, index_dir)

    elif command == "query":
        if len(sys.argv) < 3:
            print("Error: Query text required")
            sys.exit(1)

        query_text = sys.argv[2]
        num_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5

        try:
            results = MarkdownVectorizer.query_index(query_text, index_dir, num_results)

            if not results:
                print("No results found.")
            else:
                for i, result in enumerate(results):
                    print(f"\n--- Result {i+1} (Score: {result['score']:.4f}) ---")
                    print(f"Source: {result['metadata'].get('source', 'Unknown')}")
                    content = result['content']
                    if content:
                        print(f"\nContent snippet:\n{content[:300]}...")
                    else:
                        print("\nNo content available for this result.")
        except Exception as e:
            import traceback
            print(f"Error during query: {str(e)}")
            print(traceback.format_exc())

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)