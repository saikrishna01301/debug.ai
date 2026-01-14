from app.db import get_session
from app.db.crud import get_all_posts
from app.services.vector_store import VectorStore
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')


async def create_embeddings():
    """Read stack over post from db and create embeddings and add to vector db"""

    vs = VectorStore()

    try:
        # get all posts from Database
        async for session in get_session():
            posts = await get_all_posts(session)
            logging.info(f"found {len(posts)} to embed")
            if len(posts) == 0:
                logging.info("No posts found to embed")
                return

            # Process posts and create embeddings
            batch_size = 50
            # for clarity (start, end, step)
            for i in range(0, len(posts), batch_size):
                batch = posts[i : i + batch_size]

                # these are the values accepted by add_documents_batch
                texts = []
                metadatas = []
                ids = []

                for post in batch:
                    combined_text = f"Title:{post.title} Question:{post.question_body} Answer:{post.answer_body}".strip()
                    metadata = {
                        "source": "stackoverflow",
                        "question_id": post.question_id,
                        "url": post.url,
                        "tags": ", ".join(post.tags),
                        "votes": post.votes,
                        "title": post.title,
                    }

                    doc_id = f"so_{post.question_id}"

                    texts.append(combined_text)
                    metadatas.append(metadata)
                    ids.append(doc_id)

                logging.info(
                    f"Processing batch {i//batch_size + 1}/{(len(posts)-1)//batch_size + 1}..."
                )
                vs.add_documents_batch(texts, metadatas, ids)

    except Exception as e:
        logging.exception("Error creating embeddings")


if __name__ == "__main__":
    asyncio.run(create_embeddings())
