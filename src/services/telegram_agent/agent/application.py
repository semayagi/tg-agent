from typing import Any, Optional
from src.services.telegram_agent.agent.planner import Planner
from src.services.telegram_agent.agent.executor import Executor


class Agent:
    def __init__(self, planner: Planner, executor: Executor):
        self._planner = planner
        self._executor = executor

    async def run(
        self,
        query: str,
        chat: str,
        limit: int,
        thread_id: Optional[int] = None
    ) -> str:
        tools = self._planner.plan(query)

        params = {
            "chat": chat,
            "limit": limit,
            "query": query,
            "thread_id": thread_id,
        }

        results = await self._executor.execute(tools, params)

        # Combine outputs from all tools into one response
        parts = []
        for tool_name, result in results.items():
            parts.append(str(result))

        return "\n\n---\n\n".join(parts) if parts else "Агент не вернул результат."
