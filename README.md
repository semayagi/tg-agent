Track: A

# Telegram AI Agent

AI-агент, который анализирует сообщения в Telegram-чатах и отправляет гифки.

## Инструменты агента

| Инструмент | Что делает |
|---|---|
| `analyze` | Отвечает на вопрос по последним N сообщениям из чата |
| `send_gif` | Генерирует поисковый запрос через LLM -> находит гифку на Giphy -> отправляет в чат |

Планировщик (LLM) сам решает, какой инструмент вызывать — или оба сразу.

## Стек

- **python-telegram-bot** — Bot API, polling
- **OpenRouter API** — LLM (OpenAI-совместимый)
- **Giphy API** — поиск гифок
- **Python 3.11+**

## Установка и запуск

```bash
git clone <repo_url>
cd tg-agent
uv venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
uv sync
cp .env.example .env            # заполните три ключа
uv run python main.py
```

## Получение ключей

### TELEGRAM_BOT_TOKEN
1. Открыть Telegram, найти `@BotFather`
2. Написать `/newbot`, выбрать имя и username
3. Скопировать токен вида `123456789:AAB...`

**Либо попросить у меня**

### Как узнать Chat ID
Для начала добавляем бота в чат

#### Способ 1
Команда 'стат' - если написать в чат сообщение, счётчик увеличится
Позже сделаю выбор по названию чата

#### Способ 2
Добавить в этот же чат бота @Getmyid_bot - он сообщит chat ID

#### Способ 3
Написать там любое сообщение, затем открыть в браузере:
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```
Найти поле `"chat": {"id": -1001234567890}` - это и есть chat ID.

### LLM_API_KEY
Получить API_KEY своей нейросети. Есть бесплатные на openrouter.ai, я использую модель openai/gpt-oss-20b:free - если вы тоже, то в .env.example в полях LLM_MODEL и LLM_BASE_URL уже выставлены нужные значения.

### GIPHY_API_KEY
Зарегистрироваться на [developers.giphy.com](https://developers.giphy.com) -> Create App -> SDK.

## Как пользоваться

1. Добавить бота в нужный чат
2. Запустить `python main.py` — бот начинает слушать сообщения
3. Подождать пока в чат придут сообщения (или написать туда сам)
4. В CLI ввести запрос:

```
Запрос: Найди упоминания Семёна
Chat ID: -1001234567890
Топик thread_id (Enter — пропустить): 
Кол-во последних сообщений [100]: 200

Ответ агента:
В последних 200 сообщениях Семён упоминался 3 раза...
```

```
Запрос: Пришли гифку
Chat ID: -1001234567890
Топик thread_id: 42
Кол-во последних сообщений [100]: 1

Ответ агента:
Отправил гифку по запросу «confused student» в чат -1001234567890.
```

Команда `стат` показывает сколько сообщений собрано по каждому чату.

## Важно: ограничение Bot API

Бот видит только сообщения, которые пришли **пока он был в чате**. Историю до добавления бота прочитать нельзя — это ограничение Telegram Bot API. Решение: добавить бота заранее, чтобы он вникал в контекст.

## Структура проекта

```
src/services/telegram_agent/
├── adapters/
│   ├── telegram/
│   │   ├── message_store.py        # in-memory хранилище сообщений
│   │   ├── telegram_client.py      # polling бот
│   │   └── telegram_repository.py
│   ├── llm/                        # DeepSeek клиент + провайдер
│   └── giphy/                      # Giphy клиент
├── domain/
│   ├── analytics_service.py        # бизнес-логика
│   └── protocols/                  # абстракции
├── models/message.py
├── tools/
│   ├── analyze_chat.py             # Tool 1
│   └── send_gif.py                 # Tool 2
└── agent/
    ├── planner.py                  # LLM выбирает инструменты
    ├── executor.py                 # запускает инструменты
    └── application.py
main.py                             # CLI точка входа
```
