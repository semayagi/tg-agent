from typing import Optional, Protocol
from src.services.telegram_agent.models.message import Message


class TelegramRepository(Protocol):
    async def get_messages(
        self,
        chat: str,
        limit: int,
        thread_id: Optional[int] = None
    ) -> list[Message]: ...

    async def send_animation(
        self,
        chat: str,
        url: str,
        thread_id: Optional[int] = None
    ) -> None: ...
