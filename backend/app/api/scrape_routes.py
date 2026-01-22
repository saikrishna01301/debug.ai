from fastapi import APIRouter

from app.schemas.scrape import ScrapeRequest, ScrapeResponse
from app.scripts.scrape_stackoverflow import scrape_stackoverflow
from app.scripts.batch_scrape import scrape_all_tags

router = APIRouter()


@router.post("/scrape/batch")
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


@router.post("/scrape", response_model=ScrapeResponse)
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
