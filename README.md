# Telegram bot on Render (webhook)

## Шаги развёртывания

1. **Склонируйте репозиторий** или загрузите эти файлы в новый Git‑репо.

2. **Создайте бота** в @BotFather и получите токен.

3. **Настройте переменные окружения**  
   На вкладке **Environment** в Render‑сервисе добавьте:
   - `TOKEN` — токен вашего бота
   - `WEBHOOK_URL` — публичный HTTPS‑адрес сервиса, например  
     `https://telegram-bot.onrender.com`

4. **Запушьте код** на GitHub и подключите репозиторий в Render **(Web Service)**.

5. Render запустит сборку, установит зависимости и старт‑команду:  
   `python telegram_bot_webhook.py`

После запуска Render создаст веб‑хук и бот начнёт отвечать.

## Локальный запуск

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export TOKEN=...               # ваш токен
export WEBHOOK_URL=https://xxxx.ngrok-free.app   # URL туннеля
python telegram_bot_webhook.py
```

## Безопасность

Файл `.gitignore` исключает `.env`, чтобы токен бота не попал в публичный репозиторий.