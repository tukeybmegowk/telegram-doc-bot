# Telegram Doc Generator Bot

Бот, который собирает ответы пользователя, заполняет шаблон Word и отправляет PDF-файл в Telegram.

## Как запустить

1. Установить зависимости:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Положить шаблон `template.docx` рядом со скриптом.

3. Запустить:

```bash
export TELEGRAM_BOT_TOKEN=ваш_токен
python telegram_bot_document_generator.py
```

Или используйте Docker:

```bash
cp .env.example .env
docker compose up --build -d
```
