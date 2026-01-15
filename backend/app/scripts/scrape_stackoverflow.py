import httpx
import time
from datetime import datetime
from dotenv import load_dotenv
from app.db import StackOverFlowPost, get_session, init_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os
from app.db.crud import post_exists, create_post

# Load environment variables
load_dotenv()

# Get Stack Exchange API key from environment
STACKEXCHANGE_API_KEY = os.getenv("STACKEXCHANGE_API_KEY")


# Scraping Stack Overflow questions with answers
async def scrape_stackoverflow(tag: str, limit: int = 1000):
    async for session in get_session():
        logging.info(f"Scraping Stack Overflow {tag} with {limit} posts")

        # Stack Exchange API endpoint
        base_url = "https://api.stackexchange.com/2.3/questions"

        # parameters to pass
        params = {
            "key": STACKEXCHANGE_API_KEY,
            "site": "stackoverflow",
            "tagged": tag,
            "sort": "votes",
            "order": "desc",
            "filter": "withbody",  # Include question body
            "pagesize": 100,  # Max page size
        }

        posts_added = 0
        page = 1

        try:
            while posts_added < limit:
                params["page"] = page

                logging.info(f"fetching page {page}")
                response = httpx.get(base_url, params=params)

                if response.status_code != 200:
                    logging.error(f"{response.status_code}")

                data = response.json()
                questions = data.get("items", [])

                if not questions:
                    logging.error("No more questions found")
                    break

                for q in questions:
                    if posts_added >= limit:
                        break

                    # only processing accepted answer
                    if "accepted_answer_id" not in q:
                        continue

                    answer_id = q.get("accepted_answer_id")
                    answer_url = (
                        f"https://api.stackexchange.com/2.3/answers/{answer_id}"
                    )
                    answer_params = {
                        "key": STACKEXCHANGE_API_KEY,
                        "site": "stackoverflow",
                        "filter": "withbody",
                    }
                    time.sleep(0.1)
                    answer_response = httpx.get(answer_url, params=answer_params)

                    if answer_response.status_code != 200:
                        continue

                    answer_data = answer_response.json()
                    if not answer_data.get("items"):
                        continue

                    answer = answer_data["items"][0]

                    # check the question is already exists or not in db
                    is_exists = await post_exists(session, q.get("question_id"))

                    if is_exists:
                        logging.info(
                            f"Question {q.get('question_id')} already exists in knowledge"
                        )
                        continue

                    # post data to store in db
                    # combining both answer_body with question dict to store in db
                    post = {
                        "question_id": q.get("question_id"),
                        "title": q.get("title"),
                        "question_body": q.get("body"),
                        "answer_body": answer.get("body"),
                        "tags": q.get("tags", []),
                        "votes": q.get("score", 0),
                        "url": q.get("link"),
                        "created_at": datetime.fromtimestamp(q.get("creation_date")),
                    }
                    await create_post(session, post)
                    posts_added += 1

                    logging.info(
                        f"Added question {q.get('question_id')} ({posts_added}/{limit})"
                    )

                # Check if we have more pages
                if not data.get("has_more", False):
                    logging.info("No more pages available")
                    break

                page += 1
                time.sleep(0.1)  # Rate limiting between pages

        except Exception as e:
            logging.error(f"Error scraping Stack Overflow: {e}")
            raise

        logging.info(f"Scraping completed. Total posts added: {posts_added}")


if __name__ == "__main__":
    import asyncio
    import argparse

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Scrape Stack Overflow posts")
    parser.add_argument("--tag", type=str, default="python", help="Tag to scrape")
    parser.add_argument(
        "--limit", type=int, default=100, help="Number of posts to scrape"
    )

    args = parser.parse_args()

    async def main():
        # Create tables if they don't exist
        await init_db()
        # Run scraper
        await scrape_stackoverflow(args.tag, args.limit)

    # Run async scraper
    asyncio.run(main())
