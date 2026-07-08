import asyncio
from app.core.database import AsyncSessionLocal
from app.engine.intelligence_monitor import IntelligenceMonitor

async def test_monitor():
    async with AsyncSessionLocal() as db:
        monitor = IntelligenceMonitor(db)
        await monitor._poll_rss_feeds()
        await monitor.close()
        await db.commit()

if __name__ == "__main__":
    asyncio.run(test_monitor())
