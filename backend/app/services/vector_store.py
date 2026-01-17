import chromadb
import logging
import os
from typing import List, Dict
from openai import OpenAI


class VectorStore:
    def __init__(self):
        # Initialize OpenAI client for GitHub Models
        github_token = os.getenv("GITHUB_TOKEN", "").strip()
        self.embedding_client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_token,
        )
        self.model_name = "text-embedding-3-small"

        # initializing chromadb
        # PersistentClient creates chroma_db file and the vector data lives on our Disk
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="debug_knowledge",
            metadata={"description": "Stack Overflow posts and GitHub issues"},
        )

        logging.info(
            f"Vector store initialized. Total documents: {self.collection.count()}"
        )

    def add_document(self, text: str, metadata: Dict, doc_id: str):
        """
        Here, the args look like =>
        text: The content to embed
        metadata: Dict with source, url, tags, etc.
        doc_id: Unique identifier
        """

        # generating embedding
        # for testing purpose I used github models later I will change it to openai
        embedding = self._get_embedding(text)

        # add single embedding to chromadb
        self.collection.add(
            embeddings=[embedding], documents=[text], metadatas=[metadata], ids=[doc_id]
        )

        logging.info(f"Added document {doc_id} to vector store")

    def add_documents_batch(
        self, texts: List[str], metadatas: List[Dict], ids: List[str]
    ):
        # adding multiple documents at one
        logging.info(f"Generating embedding for {len(texts)} documents ")

        # generating embeddings for bunch of docs in a single API call
        embeddings = self._get_embeddings_batch(texts)

        # add all together to vector db (chromadb)
        # UPSERT ensures idempotent ingestion:
        # - update if ID exists
        # - insert if ID does not exist
        self.collection.upsert(
            embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids
        )

        logging.info(f"Added {len(texts)} documents to vector store")

    # Semantic search using embeddings

    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None):
        """
            query: Search query (e.g., error message)
        n_results: Number of results to return
        filter_metadata: Filter by metadata (e.g., {"language": "python"})
        """

        # generating embeding for query
        query_embedding = self._get_embedding(query)

        # searching in db
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
        )

        # TODO: later i need to Process and return results as needed
        # returns Dict with documents, metadatas, distances
        return result

    def get_stats(self):
        """Get statistics about the vector store"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
        }

    def _get_embedding(self, text: str):
        # Generate embedding using GitHub Models (OpenAI-compatible)
        try:
            response = self.embedding_client.embeddings.create(
                input=[text], model=self.model_name
            )

            if response.data is None:
                logging.error("Embedding API returned None for data field")
                raise ValueError("Embedding API returned None - check API key and endpoint")

            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating embedding: {str(e)}")
            raise

    def _get_embeddings_batch(self, texts: List[str]):
        """Generate embeddings for multiple texts in a single API call"""
        try:
            # The API accepts up to 2048 texts at once, but we'll process all at once for now
            response = self.embedding_client.embeddings.create(
                input=texts, model=self.model_name
            )

            if response.data is None:
                logging.error("Batch embedding API returned None for data field")
                raise ValueError("Embedding API returned None - check API key and endpoint")

            # Extract embeddings in the same order as input texts
            return [item.embedding for item in response.data]
        except Exception as e:
            logging.error(f"Error generating batch embeddings: {str(e)}")
            raise
