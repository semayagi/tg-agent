from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    id: int
    sender: str
    text: str
    date: str
    thread_id: Optional[int] = None
