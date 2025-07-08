"""
Telegram Bot: Document Generator
--------------------------------
Бот задаёт вопросы, заполняет DOCX-шаблон и присылает PDF (или DOCX fallback).
"""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Final, List, Tuple

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from docxtpl import DocxTemplate
from docx2pdf import convert as docx2pdf_convert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Плейсхолдеры и вопросы
# ---------------------------------------------------------------------------
FIELDS: Final[List[Tuple[str, str]]] = [
    ("наименование_исполнителя", "Введите *наименование исполнителя*:"),
    ("ИНН_исполнителя", "Введите *ИНН исполнителя*:"),
    ("адрес_исполнителя", "Введите *адрес исполнителя*:"),
    ("тел_исполнителя", "Введите *телефон исполнителя*:"),
    ("email", "Введите *email исполнителя*:"),
    ("№_исх", "Введите *исходящий номер (№ исх)*:"),
    ("дата_ответа", "Введите *дату ответа* (дд.мм.гггг):"),
    ("дата_претензии", "Введите *дату претензии* (дд.мм.гггг):"),
    ("дата_договора", "Введите *дату договора* (дд.мм.гггг):"),
    ("ФИО_клиента", "Введите *ФИО клиента*:"),
    ("адрес_клиента", "Введите *адрес клиента*:"),
]

STATES: Final = {i: i for i in range(len(FIELDS))}

# ---------------------------------------------------------------------------
# Хэндлеры
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["answers"] = {}
    context.user_data["state"] = 0
    await update.message.reply_text(
        "Здравствуйте! Я помогу сформировать ответ на претензию.\n"
        "Пожалуйста, ответьте на несколько вопросов.\n"
        "Для отмены введите /cancel."
    )
    await update.message.reply_text(FIELDS[0][1], parse_mode="Markdown")
    return STATES[0]


async def collect_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state: int = context.user_data["state"]
    key, _ = FIELDS[state]
    context.user_data["answers"][key] = update.message.text.strip()

    next_state = state + 1
    context.user_data["state"] = next_state

    if next_state < len(FIELDS):
        await update.message.reply_text(FIELDS[next_state][1], parse_mode="Markdown")
        return STATES[next_state]

    await update.message.reply_text("Отлично, формирую документ…")
    await generate_document(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Операция отменена. Если хотите начать заново — отправьте /start."
    )
    return ConversationHandler.END


async def generate_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answers = context.user_data["answers"]
    template_path = os.getenv("TEMPLATE_PATH", "template.docx")

    tpl = DocxTemplate(template_path)
    tpl.render(answers)

    with tempfile.TemporaryDirectory() as tmp:
        docx_path = os.path.join(tmp, "output.docx")
        pdf_path = os.path.join(tmp, "output.pdf")
        tpl.save(docx_path)

        try:
            docx2pdf_convert(docx_path, pdf_path)
            with open(pdf_path, "rb") as f:
                await update.message.reply_document(f, filename="Ответ_на_претензию.pdf")
        except Exception as exc:
            logger.warning("PDF conversion failed: %s", exc)
            with open(docx_path, "rb") as f:
                await update.message.reply_document(f, filename="Ответ_на_претензию.docx")
            await update.message.reply_text(
                "Не удалось конвертировать в PDF, отправил DOCX."
            )

# ---------------------------------------------------------------------------
# Запуск приложения
# ---------------------------------------------------------------------------
def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Environment variable TELEGRAM_BOT_TOKEN is not set")

    app = ApplicationBuilder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATES[i]: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_field)]
            for i in range(len(FIELDS))
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot is running…")
    app.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()
