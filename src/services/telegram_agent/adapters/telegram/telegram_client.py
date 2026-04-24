from typing import Optional
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes
from src.services.telegram_agent.adapters.telegram.message_store import MessageStore
from src.services.telegram_agent.models.message import Message
import requests

class TelegramBotClient:
    def __init__(self, token: str, store: MessageStore):
        self._token = token
        self._store = store
        self._app = None
        self._url = f"https://api.telegram.org/bot{token}"

    async def start(self) -> None:
        self._app = (
            ApplicationBuilder()
            .token(self._token)
            .build()
        )

        async def get_chat_information(chat_id: str | int) -> Optional[dict]:
            chat = requests.get(f"{self._url}/getChat", params={"chat_id": chat_id}).json()
            if not chat.get("ok"):
                return None
            chat = chat["result"]
            return {
                "id": chat.id,
                "title": chat.title,
                "type": chat.type
            }

        async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            # print(f"[bot] raw update: {update.to_dict()}")
            msg = update.effective_message
            if not msg or not msg.text:
                return
            chat_id = msg.chat_id
            thread_id = msg.message_thread_id
            sender = "Неизвестный"
            if msg.from_user:
                sender = (msg.from_user.first_name or "") + " " + (msg.from_user.last_name or "")
                sender = sender.strip() or msg.from_user.username or "Неизвестный"
            message = Message(
                id=msg.message_id,
                sender=sender,
                text=msg.text,
                date=msg.date.strftime("%Y-%m-%d %H:%M"),
                thread_id=thread_id,
            )
            self._store.add(chat_id, thread_id, message)
            # print(f"[bot] stored: chat={chat_id} sender={sender!r} text={msg.text!r}")

        from telegram.ext import MessageHandler, filters
        self._app.add_handler(MessageHandler(filters.TEXT, handle_update))

        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(
            drop_pending_updates=False,
            allowed_updates=["message", "edited_message", "channel_post"]
        )
        # print("[bot] Polling started")

    async def stop(self) -> None:
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    async def send_animation(self, chat_id: str | int, url: str, thread_id: Optional[int] = None) -> None:
        bot = Bot(token=self._token)
        kwargs: dict = {"chat_id": chat_id, "animation": url}
        if thread_id is not None:
            kwargs["message_thread_id"] = thread_id
        async with bot:
            await bot.send_animation(**kwargs)
