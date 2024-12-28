import json
import textwrap
import traceback
from pydoc import html

from telegram import Update
from telegram.ext import ContextTypes

from main import logger
from src import utils
from src.configs import config

DEVELOPER_CHAT_ID = config.admin['chatId']
DEVELOPER_SERVERCHAN = config.admin['serverchanId']
DEVELOPER_SERVERCHAN3 = config.admin['serverchan3Id']


# 定义消息分割函数
def split_message(text, max_length=4096):
    """
    将长消息分割成多个较短的消息，每个消息的长度不超过 max_length。
    """
    messages = []
    for line in text.split('\n'):
        wrapped_lines = textwrap.wrap(line, max_length)
        for wrapped_line in wrapped_lines:
            if len(messages) == 0 or len(messages[-1]) + len(wrapped_line) + 1 > max_length:
                # 如果当前消息太长，或者这是第一条新消息，则创建一个新消息
                messages.append(wrapped_line)
            else:
                # 否则，将当前行添加到上一条消息中，并添加一个换行符
                messages[-1] += '\n' + wrapped_line
    return messages


def get_long_message_head_tail(text, max_length=4070) -> list[str]:
    messages = ["<pre>" + text[:max_length] + "</pre>"]
    while len(text) > max_length:
        text = text[max_length:]
        messages.append("<pre>" + text[:max_length] + "</pre>")
    return messages

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n\n\n "
        f"```python \nupdate = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}\n\n"
        f"context.chat_data = {html.escape(str(context.chat_data))}\n\n"
        f"context.user_data = {html.escape(str(context.user_data))}\n\n"
        f"{html.escape(tb_string)}```"
    )

    error_message = html.escape(tb_string)
    error_str = f"<pre>update = {error_message}</pre>\n\n"
    logger.warning("error_str length: " + str(len(error_str)))
    logger.warning("error_str: \n" + message)

    messages = [
        (f"An exception was raised while handling an update\n"
         f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
         f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n")
    ]

    messages.extend(
        get_long_message_head_tail(f"update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"))
    messages.extend(get_long_message_head_tail(f"{html.escape(tb_string)}"))

    # messages = split_message(message)

    # for msg in messages:
    #     # Finally, send the msg
    #     if msg:
    #         await context.bot.send_message(
    #             chat_id=DEVELOPER_CHAT_ID, text=msg, parse_mode=ParseMode.HTML
    #         )

    # utils.send_serverchan(DEVELOPER_SERVERCHAN, "tgbot message", message)
    utils.send_serverchan_3(DEVELOPER_SERVERCHAN3, "tgbot message", message)


async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]
