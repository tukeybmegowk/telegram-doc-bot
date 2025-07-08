import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    AIORateLimiter,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

TOKEN = os.environ["TOKEN"]  # задайте через переменные окружения в Render

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    await update.message.reply_text(
        "Привет! Я бот. Отправь мне любое сообщение — я повторю его."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Эхо на любое текстовое сообщение"""
    await update.message.reply_text(update.message.text)

def main() -> None:
    # ограничитель запросов PTB, иначе Render может выдать 429
    app = (
        Application.builder()
        .token(TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    port = int(os.environ.get("PORT", 10000))
    url_path = TOKEN  # уникальный путь веб‑хука
    external_url = (
        os.environ.get("WEBHOOK_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
    )
    if not external_url:
        raise RuntimeError(
            "Укажите WEBHOOK_URL (или доверьтесь переменной RENDER_EXTERNAL_URL)"
        )

    webhook_url = f"{external_url.rstrip('/')}/{url_path}"

    logger.info("Запускаю webhook на 0.0.0.0:%s ⇒ %s", port, webhook_url)

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=url_path,
        webhook_url=webhook_url,
        stop_signals=None,
    )


if __name__ == "__main__":
    main()