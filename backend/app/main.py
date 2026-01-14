import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.services.parser import ErrorParser
from app.services.vector_store import VectorStore
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
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


@app.post("/api/search")
def search_knowledge_base(request: SearchRequest):
    # Parse error log to extract meaningful search terms
    parsed_error = parser.parse(request.query)

    # Create better search query from parsed error
    if parsed_error.get("error_type") and parsed_error.get("error_message"):
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

    llm_response = llm.analyze_error(parsed_error, search_results_dicts)

    return llm_response
