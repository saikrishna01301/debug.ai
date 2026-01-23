import logging
import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.crud import create_parsed_error, create_analysis
from app.services.parser import ErrorParser
from app.services.supabase_vector_store import SupabaseVectorStore
from app.services.cache import CacheService
from app.services.llm_analyzer import LLMAnalyzer
from app.schemas.search import SearchRequest, SearchResult
from app.schemas.analysis import AnalysisResponse


router = APIRouter()

parser = ErrorParser()
vc = SupabaseVectorStore()
llm = LLMAnalyzer()
cache = CacheService()


@router.post("/analyze")
async def analyze_error(
    request: SearchRequest, session: AsyncSession = Depends(get_session)
):
    start_time = time.time()

    # Check cache first
    cached_analysis = cache.get_analysis(request.query)
    if cached_analysis:
        analysis_time_ms = int((time.time() - start_time) * 1000)
        logging.info(f"Returning cached analysis in {analysis_time_ms}ms")
        cached_analysis["analysis_time_ms"] = analysis_time_ms
        return AnalysisResponse(**cached_analysis)

    # Parse error log to extract meaningful search terms
    parsed_error = parser.parse(request.query)

    # Create better search query from parsed error
    if (
        parsed_error
        and parsed_error.get("error_type")
        and parsed_error.get("error_message")
    ):
        search_query = f"{parsed_error['error_type']}: {parsed_error['error_message']}"
        # Search knowledge base (with cache)
        cached_search = cache.get_search_results(search_query)
    else:
        search_query = request.query
        cached_search = None

    if cached_search:
        search_results = cached_search
    else:
        # Perform vector search in Supabase
        results = await vc.search(
            search_query, n_results=min(request.limit, 3)
        )  # Max 3 for faster response

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
        # Cache search results
        cache.set_search_results(search_query, search_results)

    logging.info(
        f"Found {len(search_results)} relevant results (threshold: {RELEVANCE_THRESHOLD})"
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
            "line_number": None,
            "raw_error_log": request.query,
        }

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

    # Cache the analysis result
    cache.set_analysis(
        request.query,
        {
            "error_type": parsed_error.get("error_type"),
            "error_message": parsed_error.get("error_message"),
            "language": parsed_error.get("language", "unknown"),
            "file_path": parsed_error.get("file_path"),
            "line_number": parsed_error.get("line_number"),
            "root_cause": llm_response.get("root_cause", ""),
            "reasoning": llm_response.get("reasoning", ""),
            "solutions": llm_response.get("solutions", []),
            "sources_used": len(search_results),
            "analysis_id": db_analysis.id,
        },
    )

    # Calculate analysis time
    analysis_time_ms = int((time.time() - start_time) * 1000)
    logging.info(f"Analysis completed in {analysis_time_ms}ms")

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
        analysis_id=db_analysis.id,
        analysis_time_ms=analysis_time_ms,
    )

    return analysis_result
