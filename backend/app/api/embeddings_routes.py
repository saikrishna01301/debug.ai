from fastapi import APIRouter

from app.scripts.create_embeddings import create_embeddings

router = APIRouter()


@router.post("/embeddings/create")
async def create_embeddings_endpoint():
    """
    Create embeddings for all Stack Overflow posts in the database.

    This will:
    1. Fetch all posts from the database
    2. Generate embeddings using OpenAI
    3. Store them in ChromaDB vector store

    **Note**: This processes posts in batches of 500 for efficiency.
    """
    try:
        await create_embeddings()
        return {
            "status": "success",
            "message": "Embeddings created successfully for all posts"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create embeddings: {str(e)}",
            "error": str(e)
        }
