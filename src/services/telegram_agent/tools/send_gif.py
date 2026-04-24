from typing import Optional
from src.services.telegram_agent.domain.analytics_service import AnalyticsService
from src.services.telegram_agent.domain.protocols.telegram_repository import TelegramRepository
from src.services.telegram_agent.adapters.giphy.giphy_client import GiphyClient


class SendGifTool:
    """
    Generates a contextual GIF search query via LLM,
    finds a GIF on Giphy, and sends it to the specified chat/topic.
    """

    def __init__(
        self,
        analytics: AnalyticsService,
        telegram_repo: TelegramRepository,
        giphy: GiphyClient
    ):
        self._analytics = analytics
        self._repo = telegram_repo
        self._giphy = giphy

    async def run(self, params: dict) -> str:
        chat: str = params["chat"]
        context: str = params.get("query", "funny moment")
        thread_id: Optional[int] = params.get("thread_id")

        # Step 1: LLM generates a search phrase in English
        search_query = await self._analytics.generate_gif_query(context)

        # Step 2: Giphy returns the URL
        gif_url = self._giphy.search(search_query)
        if not gif_url:
            return f"Не нашёл гифку по запросу «{search_query}». Попробуй другой контекст."

        # Step 3: Send to Telegram
        await self._repo.send_animation(chat, gif_url, thread_id)
        return f"Отправил гифку по запросу «{search_query}» в чат {chat}."
