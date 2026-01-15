import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import init_db
from app.db.session import get_session
from app.db.crud import create_parsed_error, create_analysis
from app.services.parser import ErrorParser
from app.services.vector_store import VectorStore
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.schemas.analysis import AnalysisResponse
from app.services.llm_analyzer import LLMAnalyzer

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

    results = vc.search(search_query, n_results=request.limit)

    search_results = []
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
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
