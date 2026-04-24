from src.services.telegram_agent.domain.protocols.telegram_repository import TelegramRepository
from src.services.telegram_agent.domain.protocols.llm_provider import LLMProvider
from src.services.telegram_agent.models.message import Message
from typing import Optional


class AnalyticsService:
    def __init__(self, telegram_repo: TelegramRepository, llm: LLMProvider):
        self._repo = telegram_repo
        self._llm = llm

    async def analyze_chat(
        self,
        chat: str,
        limit: int,
        query: str,
        thread_id: Optional[int] = None
    ) -> str:
        messages = await self._repo.get_messages(chat, limit, thread_id)

        if not messages:
            return "Сообщений не найдено в указанном чате/топике."

        formatted = self._format_messages(messages)

        prompt = f"""Ты — аналитик Telegram-переписки. Тебе дали последние {len(messages)} сообщений из чата.

Задача пользователя: {query}

Сообщения (формат: [дата] Автор: текст):
{formatted}

Выполни задачу пользователя на основе этих сообщений. Если запрошенного нет — честно скажи об этом.
Отвечай на русском языке, структурированно."""

        return self._llm.generate_response(prompt)

    def _format_messages(self, messages: list[Message]) -> str:
        lines = []
        for msg in messages:
            text = msg.text or "[медиа без текста]"
            lines.append(f"[{msg.date}] {msg.sender}: {text}")
        return "\n".join(lines)

    async def generate_gif_query(self, context: str) -> str:
        prompt = f"""На основе этого контекста придумай короткую поисковую фразу на английском для поиска смешной/подходящей гифки (2-4 слова).
Контекст: {context}
Верни ТОЛЬКО фразу для поиска, без кавычек и объяснений."""
        return self._llm.generate_response(prompt).strip()
