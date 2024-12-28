import logging
from uuid import uuid4

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters, InlineQueryHandler, \
    Updater

from src import mybot, my_log

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = my_log.logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = [InlineQueryResultArticle(
        id=str(uuid4()),
        title='Caps',
        input_message_content=InputTextMessageContent(query.upper())
    )]
    await context.bot.answer_inline_query(update.inline_query.id, results)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


# if __name__ == '__main__':
#
#     # application = ApplicationBuilder().token('8123613382:AAFmKlDhd95FuGJqmujkuA-njp-sR9N4iHI').proxy_url("https://127.0.0.1:7890").build()
#     application = ApplicationBuilder().token('7608341001:AAGZ45XLr6Hm9nDiBxB08C1VMOAxiaDD5Wc').build()
#
#     # application.process_update()
#
#     start_handler = CommandHandler('start', start)
#     echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
#     caps_handler = CommandHandler('caps', caps)
#     inline_caps_handler = InlineQueryHandler(inline_caps)
#
#     application.add_handler(start_handler)
#     application.add_handler(echo_handler)
#     application.add_handler(caps_handler)
#     application.add_handler(inline_caps_handler)
#
#     # Other handlers
#     unknown_handler = MessageHandler(filters.COMMAND, unknown)
#     application.add_handler(unknown_handler)
#
#     application.run_polling()

def get_long_message_head_tail(text, max_length=4000) -> list[str]:
    messages = ["" + text[:max_length] + ""]
    while len(text) > max_length:
        text = text[max_length:]
        messages.append("" + text[:max_length] + "")
    return messages


if __name__ == '__main__':
    mybot.run()

