import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import init_db
from app.db.session import get_session
from app.db.crud import create_parsed_error, create_analysis
from app.services.parser import ErrorParser
from app.services.vector_store import VectorStore
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.schemas.analysis import AnalysisResponse
from app.schemas.scrape import ScrapeRequest, ScrapeResponse
from app.services.llm_analyzer import LLMAnalyzer
from app.scripts.scrape_stackoverflow import scrape_stackoverflow
from app.scripts.batch_scrape import scrape_all_tags
from app.scripts.create_embeddings import create_embeddings

# Load environment variables
load_dotenv()

# Configure logging for the entire application
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DebugAI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ErrorParser()
vc = VectorStore()
llm = LLMAnalyzer()


# Run this function exactly once, when the application first starts up
@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():

    return {"message": "Welcome to DebugAI API with Supabase"}


@app.post("/api/analyze")
async def analyze_error(request: SearchRequest, session: AsyncSession = Depends(get_session)):
    # Parse error log to extract meaningful search terms
    parsed_error = parser.parse(request.query)

    # Create better search query from parsed error
    if parsed_error and parsed_error.get("error_type") and parsed_error.get("error_message"):
        search_query = f"{parsed_error['error_type']}: {parsed_error['error_message']}"
    else:
        search_query = request.query

    results = vc.search(search_query, n_results=min(request.limit, 3))  # Max 3 for faster response

    # Filter results by relevance threshold (distance < 0.6 means relevant)
    RELEVANCE_THRESHOLD = 0.6
    search_results = []
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        # Only include results that are actually relevant
        if distance < RELEVANCE_THRESHOLD:
            search_results.append(
                SearchResult(
                    title=meta["title"],
                    url=meta["url"],
                    content=doc[:500],  # First 500 chars
                    tags=(
                        meta["tags"].split(", ")
                        if isinstance(meta["tags"], str)
                        else meta["tags"]
                    ),
                    votes=meta["votes"],
                    distance=distance,
                )
            )

    logging.info(f"Found {len(search_results)} relevant results (threshold: {RELEVANCE_THRESHOLD})")

    # Convert SearchResult objects to dicts for LLM analyzer
    search_results_dicts = [result.dict() for result in search_results]

    # If parser failed, create a minimal parsed_error structure
    if not parsed_error:
        parsed_error = {
            "error_type": "Unknown",
            "error_message": request.query,
            "language": "unknown",
            "file_path": None,
            "line_number": None
        }

    # Add raw_error_log to parsed_error for database storage
    parsed_error["raw_error_log"] = request.query

    # Store parsed error in database
    db_error = await create_parsed_error(session, parsed_error)

    llm_response = llm.analyze_error(parsed_error, search_results_dicts)

    # Store analysis in database
    analysis_data = {
        "parsed_error_id": db_error.id,
        "root_cause": llm_response.get("root_cause", ""),
        "reasoning": llm_response.get("reasoning", ""),
        "solutions": llm_response.get("solutions", []),
        "sources_used": len(search_results),
    }
    db_analysis = await create_analysis(session, analysis_data)

    # Combine parsed error info with LLM analysis
    analysis_result = AnalysisResponse(
        error_type=parsed_error.get("error_type"),
        error_message=parsed_error.get("error_message"),
        language=parsed_error.get("language", "unknown"),
        file_path=parsed_error.get("file_path"),
        line_number=parsed_error.get("line_number"),
        root_cause=llm_response.get("root_cause", ""),
        reasoning=llm_response.get("reasoning", ""),
        solutions=llm_response.get("solutions", []),
        sources_used=len(search_results),
        analysis_id=db_analysis.id
    )

    return analysis_result


@app.post("/api/scrape/batch")
async def batch_scrape():
    """
    Scrape multiple Stack Overflow tags in one go.

    This will scrape:
    - Python: 500 posts
    - JavaScript: 500 posts
    - React: 300 posts
    - TypeScript: 300 posts
    - Node.js: 200 posts
    - Django: 150 posts
    - FastAPI: 100 posts

    Total: 2,050 posts across 7 tags
    """
    try:
        result = await scrape_all_tags()
        return {
            "status": "success",
            "message": f"Batch scrape completed: {result['total_scraped']}/{result['total_target']} posts",
            "total_scraped": result['total_scraped'],
            "total_target": result['total_target'],
            "tags_count": result['tags_count']
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Batch scrape failed: {str(e)}",
            "error": str(e)
        }


@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_posts(request: ScrapeRequest):
    """
    Scrape Stack Overflow posts for a specific tag.

    You can specify any tag and the number of posts you want to scrape (1-1000).

    **Common tags**: python, javascript, react, typescript, node.js, django, fastapi, java, go, rust
    """
    try:
        await scrape_stackoverflow(request.tag, request.limit)
        return ScrapeResponse(
            status="success",
            message=f"Successfully scraped {request.limit} posts for tag: {request.tag}",
            tag=request.tag,
            posts_scraped=request.limit
        )
    except Exception as e:
        return ScrapeResponse(
            status="error",
            message=f"Failed to scrape posts",
            tag=request.tag,
            error=str(e)
        )


@app.post("/api/embeddings/create")
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
