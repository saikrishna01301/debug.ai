import logging
from app.scripts.scrape_stackoverflow import scrape_stackoverflow
import asyncio


async def scrape_all_tags():
    """
    Scrape multiple tags to build comprehensive knowledge base
    """
    tags_to_scrape = [
        ("python", 500),
        ("javascript", 500),
        ("react", 300),
        ("typescript", 300),
        ("node.js", 200),
        ("django", 150),
        ("fastapi", 100),
    ]

    total_scraped = 0
    total_target = sum(limit for _, limit in tags_to_scrape)

    logging.info(f"Starting batch scrape: {len(tags_to_scrape)} tags, target: {total_target} posts")

    for tag, limit in tags_to_scrape:
        try:
            logging.info(f"Scraping {tag}: {limit} posts")
            await scrape_stackoverflow(tag, limit)
            total_scraped += limit
            # Wait between tags to be polite to API
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Error scraping {tag}: {e}")
            continue

    logging.info(f"Batch scrape complete: {total_scraped}/{total_target} posts")
    return {
        "total_scraped": total_scraped,
        "total_target": total_target,
        "tags_count": len(tags_to_scrape)
    }
