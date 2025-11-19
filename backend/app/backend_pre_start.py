import asyncio
import logging
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log

from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DSN_ASYNC = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

max_tries = 60 * 5
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
    reraise=True,
)
async def init(dsn: str) -> None:
    async_engine = create_async_engine(dsn, pool_pre_ping=True)
    try:
        async with AsyncSession(async_engine) as session:
            await session.execute(select(text("1")))
    finally:
        await async_engine.dispose()


def main() -> None:
    logger.info("Initializing service (async local engine)")
    asyncio.run(init(DSN_ASYNC))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
