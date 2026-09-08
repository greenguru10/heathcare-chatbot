import asyncio
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger


class UptimeKeepAliveBot:
    """
    Automated Background Uptime Bot to keep free/starter tier cloud instances
    (e.g., Render, Railway, Fly.io) awake 24/7 by periodically pinging health endpoints.
    """
    def __init__(self):
        self.is_running = False
        self._task = None

    async def _ping_loop(self):
        # Initial grace period before first ping
        await asyncio.sleep(45)
        
        interval_seconds = max(60, settings.UPTIME_PING_INTERVAL_MINUTES * 60)
        target_url = settings.UPTIME_PING_URL or "http://localhost:8000/api/v1/health"

        logger.info("Uptime Keep-Alive Bot active", target_url=target_url, interval_minutes=settings.UPTIME_PING_INTERVAL_MINUTES)

        async with httpx.AsyncClient(timeout=15.0) as client:
            while self.is_running:
                try:
                    res = await client.get(target_url)
                    if res.status_code == 200:
                        logger.info("Uptime Bot ping successful", url=target_url, status_code=res.status_code)
                    else:
                        logger.warn("Uptime Bot ping returned non-200", url=target_url, status_code=res.status_code)
                except Exception as err:
                    logger.debug("Uptime Bot ping notice (expected during cold starts)", error=str(err))

                # Sleep until next scheduled ping
                await asyncio.sleep(interval_seconds)

    def start(self):
        if settings.UPTIME_BOT_ENABLED and not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._ping_loop())
            logger.info("Started Uptime Keep-Alive Bot background loop")

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            logger.info("Stopped Uptime Keep-Alive Bot")


uptime_bot = UptimeKeepAliveBot()
