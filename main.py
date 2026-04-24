import asyncio
import sys
from loguru import logger
from src.services.telegram_agent.config import Settings
from src.services.telegram_agent.adapters.telegram.message_store import MessageStore
from src.services.telegram_agent.adapters.telegram.telegram_client import TelegramBotClient
from src.services.telegram_agent.adapters.telegram.telegram_repository import TelegramRepositoryImplementation
from src.services.telegram_agent.adapters.llm.deepseek_client import LLMClient
from src.services.telegram_agent.adapters.llm.deepseek_provider import LLMProvider
from src.services.telegram_agent.adapters.giphy.giphy_client import GiphyClient
from src.services.telegram_agent.domain.analytics_service import AnalyticsService
from src.services.telegram_agent.tools.analyze_chat import AnalyzeChatTool
from src.services.telegram_agent.tools.send_gif import SendGifTool
from src.services.telegram_agent.agent.planner import Planner
from src.services.telegram_agent.agent.executor import Executor
from src.services.telegram_agent.agent.application import Agent

MAX_HISTORY_CHECK = 500


def prompt(question: str, default=None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    try:
        answer = input(f"{question}{suffix}: ").strip()
    except EOFError:
        return str(default) if default is not None else ""
    return answer if answer else (str(default) if default is not None else "")


def prompt_int(question: str, default=None) -> int | None:
    raw = prompt(question, default)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        print(f"  Ожидается число, получено «{raw}». Попробуй снова.")
        return prompt_int(question, default)


async def cli_loop(agent: Agent, store: MessageStore) -> None:
    """Runs CLI in a separate thread so it doesn't block the event loop."""
    loop = asyncio.get_event_loop()

    def blocking_cli() -> None:
        print("\n=== Telegram AI Agent ===")
        print("Бот слушает чаты в фоне.")
        print("Возможности: анализировать чат, отправить гифку - просто введите произвольный запрос")
        print("Команды: 'выход' — завершить\n")

        while True:
            print("-" * 42)
            query = prompt("Запрос")
            if not query:
                continue
            if query.lower() in ("выход", "exit", "quit", "q"):
                asyncio.run_coroutine_threadsafe(
                    asyncio.coroutine_stop(), loop
                )
                break
            if query.lower() in ("стат", "stat", "stats"):
                print(f"  Собрано: {store.stats()}")
                continue

            chat_raw = prompt("Chat ID (число, например -1001234567890)")
            if not chat_raw:
                print("  Chat ID не указан.")
                continue
            try:
                chat_id = int(chat_raw)
            except ValueError:
                print("  Chat ID должен быть числом.")
                continue

            thread_id = prompt_int("Топик thread_id (Enter — пропустить)")
            limit = prompt_int("Кол-во последних сообщений", default=100) or 100

            available = len(store.get(chat_id, MAX_HISTORY_CHECK, thread_id))
            if available == 0:
                print(f"\n  Для чата {chat_id} сообщений пока нет. Напиши что-нибудь в чат.\n")
                continue

            print(f"\n  Доступно: {available} сообщений. Анализирую...\n")

            future = asyncio.run_coroutine_threadsafe(
                agent.run(query=query, chat=str(chat_id), limit=limit, thread_id=thread_id),
                loop
            )
            try:
                result = future.result(timeout=60)
                print(f"\nОтвет агента:\n{result}\n")
            except Exception as e:
                print(f"\nОшибка: {e}\n")

    await loop.run_in_executor(None, blocking_cli)


async def _run(settings: Settings) -> None:
    store = MessageStore()

    tg_client = TelegramBotClient(token=settings.telegram_bot_token, store=store)
    await tg_client.start()

    tg_repo = TelegramRepositoryImplementation(tg_client, store)
    ds_client = LLMClient(api_key=settings.llm_api_key, model=settings.llm_model, base_url=settings.llm_base_url)
    llm = LLMProvider(ds_client)
    giphy = GiphyClient(api_key=settings.giphy_api_key)
    analytics = AnalyticsService(tg_repo, llm)

    tools = {
        "analyze": AnalyzeChatTool(analytics),
        "send_gif": SendGifTool(analytics, tg_repo, giphy),
    }

    executor = Executor(tools)
    planner = Planner(llm)
    agent = Agent(planner, executor)

    try:
        await cli_loop(agent, store)
    finally:
        await tg_client.stop()
        print("До свидания!")


def main() -> None:
    logger.remove()
    logger.add(sys.stderr, level="WARNING", format="{level} | {name} | {message}")
    settings = Settings()
    asyncio.run(_run(settings))


if __name__ == "__main__":
    main()