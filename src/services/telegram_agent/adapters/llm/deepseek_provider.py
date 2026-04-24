from src.services.telegram_agent.adapters.llm.deepseek_client import LLMClient


class LLMProvider:
    def __init__(self, client: LLMClient):
        self._client = client

    def generate_response(self, prompt: str) -> str:
        return self._client.create_chat_completion(prompt)
