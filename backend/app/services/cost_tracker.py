import logging
from app.db.crud import create_cost_record, total_cost, daily_costs, cost_breakdown
from sqlalchemy.ext.asyncio import AsyncSession


class CostTracker:
    """
    Track OpenAI API costs

    The Prices used in here is as of Jan 2025.
    """

    # Pricing per 1M tokens
    PRICING = {
        "gpt-4o-mini": {
            "prompt": 0.150,  # $0.150 per 1M prompt tokens
            "completion": 0.600,  # $0.600 per 1M completion tokens
        },
        "gpt-4-turbo-preview": {"prompt": 10.00, "completion": 30.00},
        "text-embedding-3-small": {
            "prompt": 0.020,  # $0.020 per 1M tokens
            "completion": 0.0,
        },
    }

    # Track embedding cost
    async def track_embedding(self, session: AsyncSession, tokens: int):
        model = "text-embedding-3-small"
        cost = (tokens / 1_000_000) * self.PRICING[model]["prompt"]

        await create_cost_record(
            session=session,
            operation="embedding",
            model=model,
            cost=cost,
            prompt_tokens=tokens,
            total_tokens=tokens,
        )

        logging.info(f"Analysis cost: ${cost:.6f} ({tokens} tokens)")

    # Track LLM analysis cost
    async def track_analysis(
        self,
        session: AsyncSession,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
    ):
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        total_cost = prompt_cost + completion_cost

        await create_cost_record(
            session=session,
            operation="analysis",
            model=model,
            cost=total_cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

        logging.info(
            f"Analysis cost: ${total_cost:.6f} ({prompt_tokens} prompt + {completion_tokens} completion tokens)"
        )

async def get_total_cost(session: AsyncSession, days: int = 30) -> float:
    return await total_cost(session, days)


async def get_daily_costs(session: AsyncSession, days: int = 7) -> list:
    return await daily_costs(session, days)


async def get_cost_breakdown(session: AsyncSession, days: int = 30) -> list:
    return await cost_breakdown(session, days)