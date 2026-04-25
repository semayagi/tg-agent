# Прослойка над клиентом, дающая доступ к нужным извне методам
from typing import Optional
from src.services.telegram_agent.adapters.telegram.telegram_client import TelegramBotClient
from src.services.telegram_agent.adapters.telegram.message_store import MessageStore
from src.services.telegram_agent.models.message import Message


class TelegramRepositoryImplementation:
    def __init__(self, client: TelegramBotClient, store: MessageStore):
        self._client = client
        self._store = store

    async def get_messages(
        self,
        chat: str | int,
        limit: int,
        thread_id: Optional[int] = None,
    ) -> list[Message]:
        return self._store.get(int(chat), limit, thread_id)

    async def send_animation(
        self,
        chat: str | int,
        url: str,
        thread_id: Optional[int] = None,
    ) -> None:
        await self._client.send_animation(chat, url, thread_id)
