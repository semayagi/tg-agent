from typing import Any


class Executor:
    """Runs the tools selected by the Planner."""

    def __init__(self, tools: dict):
        self._tools = tools

    async def execute(self, tool_names: list[str], params: dict[str, Any]) -> dict:
        results = {}
        for name in tool_names:
            if name in self._tools:
                results[name] = await self._tools[name].run(params)
            else:
                results[name] = f"[Инструмент '{name}' не найден]"
        return results
