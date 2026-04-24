from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://openrouter.ai/api/v1/"):
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self._model = model

    def create_chat_completion(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
