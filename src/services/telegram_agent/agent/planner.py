import json
from src.services.telegram_agent.domain.protocols.llm_provider import LLMProvider


class Planner:
    """Decides which tools to invoke based on the user's query."""

    def __init__(self, llm: LLMProvider):
        self._llm = llm

    def plan(self, query: str) -> list[str]:
        prompt = f"""Ты — планировщик AI-агента для Telegram.
Доступные инструменты:
- "analyze" — читает сообщения из чата и отвечает на вопрос по ним
- "send_gif" — отправляет гифку в чат

Верни ТОЛЬКО JSON-массив с именами инструментов, которые нужно вызвать.
Примеры:
  "Найди упоминания Семёна" -> ["analyze"]
  "Пришли гифку" -> ["send_gif"]
  "Проанализируй и пришли гифку" -> ["analyze", "send_gif"]

Запрос: {query}"""

        response = self._llm.generate_response(prompt)
        try:
            result = json.loads(response.strip())
            if isinstance(result, list):
                return result
        except Exception:
            pass
        # Fallback: if LLM confused — default to analyze
        return ["analyze"]
