from typing import Optional
from src.services.telegram_agent.domain.analytics_service import AnalyticsService


class AnalyzeChatTool:
    """
    Reads last `limit` messages from a chat (optionally a topic/thread)
    and answers the user's query using LLM.
    """

    def __init__(self, analytics: AnalyticsService):
        self._analytics = analytics

    async def run(self, params: dict) -> str:
        chat: str = params["chat"]
        limit: int = params["limit"]
        query: str = params["query"]
        thread_id: Optional[int] = params.get("thread_id")

        return await self._analytics.analyze_chat(chat, limit, query, thread_id)
