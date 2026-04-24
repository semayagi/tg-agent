import threading
from collections import defaultdict, deque
from src.services.telegram_agent.models.message import Message

# Max messages to keep per (chat_id, thread_id) pair
MAX_HISTORY = 500


class MessageStore:
    """
    Thread-safe in-memory store.
    The polling bot writes here; the agent reads from here.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # key: (chat_id, thread_id_or_None) -> deque of Message
        self._store: dict[tuple, deque] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

    def add(self, chat_id: int, thread_id: int | None, message: Message) -> None:
        with self._lock:
            self._store[(chat_id, thread_id)].appendleft(message)

    def get(self, chat_id: int | str, limit: int, thread_id: int | None = None) -> list[Message]:
        key = (int(chat_id), thread_id)
        with self._lock:
            msgs = list(self._store[key])
        return msgs[:limit]

    def stats(self) -> dict:
        with self._lock:
            return {str(k): len(v) for k, v in self._store.items()}
