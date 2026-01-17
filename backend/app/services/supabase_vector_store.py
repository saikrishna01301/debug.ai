import logging
import os
import json
from typing import List, Dict
from openai import OpenAI
from sqlalchemy import text
from app.db.session import get_session


class SupabaseVectorStore:
    """Vector store using Supabase pgvector for persistent storage"""

    def __init__(self):
        # Initialize OpenAI client for GitHub Models
        github_token = os.getenv("GITHUB_TOKEN", "").strip()

        # Validate token
        if not github_token:
            logging.error("GITHUB_TOKEN environment variable is not set!")
            raise ValueError("GITHUB_TOKEN is required but not found in environment")

        # Log token prefix for debugging (never log the full token)
        token_prefix = github_token[:20] if len(github_token) > 20 else github_token[:10]
        logging.info(f"Initializing with GitHub token prefix: {token_prefix}...")

        self.embedding_client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_token,
        )
        self.model_name = "text-embedding-3-small"
        logging.info(f"Supabase Vector store initialized with model: {self.model_name}")

    async def add_document(self, text: str, metadata: Dict, doc_id: str):
        """
        Add a single document with its embedding to Supabase

        Args:
            text: The content to embed
            metadata: Dict with source, url, tags, etc.
            doc_id: Unique identifier
        """
        # Generate embedding
        embedding = self._get_embedding(text)

        # Convert embedding list to PostgreSQL array format
        embedding_str = f"[{','.join(map(str, embedding))}]"
        metadata_json = json.dumps(metadata)

        # Store in Supabase using raw SQL
        async for session in get_session():
            query = text("""
                INSERT INTO embeddings (id, content, embedding, metadata)
                VALUES (:id, :content, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
            """)

            await session.execute(
                query,
                {
                    "id": doc_id,
                    "content": text,
                    "embedding": embedding_str,
                    "metadata": metadata_json
                }
            )
            await session.commit()

        logging.info(f"Added document {doc_id} to Supabase vector store")

    async def add_documents_batch(
        self, texts: List[str], metadatas: List[Dict], ids: List[str]
    ):
        """Add multiple documents at once (more efficient)"""
        logging.info(f"Generating embeddings for {len(texts)} documents")

        # Generate embeddings for all texts in one API call
        embeddings = self._get_embeddings_batch(texts)

        # Prepare batch insert
        async for session in get_session():
            for doc_id, text_content, embedding, metadata in zip(ids, texts, embeddings, metadatas):
                embedding_str = f"[{','.join(map(str, embedding))}]"
                metadata_json = json.dumps(metadata)

                query = text("""
                    INSERT INTO embeddings (id, content, embedding, metadata)
                    VALUES (:id, :content, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """)

                await session.execute(
                    query,
                    {
                        "id": doc_id,
                        "content": text_content,
                        "embedding": embedding_str,
                        "metadata": metadata_json
                    }
                )

            await session.commit()

        logging.info(f"Added {len(texts)} documents to Supabase vector store")

    async def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None):
        """
        Semantic search using cosine similarity

        Args:
            query: Search query (e.g., error message)
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (not implemented yet)

        Returns:
            Dict with documents, metadatas, and distances (compatible with ChromaDB format)
        """
        # Generate embedding for query
        query_embedding = self._get_embedding(query)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        # Search using cosine distance (1 - cosine_similarity)
        # Lower distance = more similar
        async for session in get_session():
            query_sql = text("""
                SELECT
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity,
                    embedding <=> CAST(:query_embedding AS vector) as distance
                FROM embeddings
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)

            result = await session.execute(
                query_sql,
                {
                    "query_embedding": embedding_str,
                    "limit": n_results
                }
            )

            rows = result.fetchall()

            # Format results to match ChromaDB format for compatibility
            documents = [[row.content for row in rows]]
            metadatas = [[row.metadata for row in rows]]
            distances = [[row.distance for row in rows]]
            ids = [[row.id for row in rows]]

            return {
                "documents": documents,
                "metadatas": metadatas,
                "distances": distances,
                "ids": ids
            }

    async def get_stats(self):
        """Get statistics about the vector store"""
        async for session in get_session():
            result = await session.execute(text("SELECT COUNT(*) FROM embeddings"))
            count = result.scalar()

            return {
                "total_documents": count,
                "store_type": "supabase_pgvector"
            }

    def _get_embedding(self, text: str):
        """Generate embedding using GitHub Models (OpenAI-compatible)"""
        try:
            response = self.embedding_client.embeddings.create(
                input=[text], model=self.model_name
            )

            # Debug logging
            logging.info(f"Embedding API response type: {type(response)}")
            logging.info(f"Embedding API response: {response}")

            if response.data is None:
                logging.error("Embedding API returned None for data field")
                raise ValueError("Embedding API returned None - check API key and endpoint")

            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating embedding: {str(e)}")
            logging.error(f"Error type: {type(e)}")
            raise

    def _get_embeddings_batch(self, texts: List[str]):
        """Generate embeddings for multiple texts in a single API call"""
        try:
            response = self.embedding_client.embeddings.create(
                input=texts, model=self.model_name
            )

            if response.data is None:
                logging.error("Batch embedding API returned None for data field")
                raise ValueError("Embedding API returned None - check API key and endpoint")

            return [item.embedding for item in response.data]
        except Exception as e:
            logging.error(f"Error generating batch embeddings: {str(e)}")
            raise
