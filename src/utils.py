from datetime import datetime

from serverchan_sdk import sc_send

from main import logger
from src.configs.channel_type import ChannelType
from src.configs.user_info import UserInfo

import pytz


def get_nowtime() -> datetime:
    nowtime = datetime.now(pytz.timezone('Asia/Shanghai'))
    return nowtime


def get_today_str()-> str:
    nowtime = get_nowtime()
    return f"{nowtime.year}.{nowtime.month}.{nowtime.day}"


def send_serverchan_3(sendkey: str, title, desp='', options=None):
    print("send serverchan_3 message")
    resource = sc_send(sendkey, title, desp, options)
    return resource


def send_serverchan(sendkey: str, title, desp='', options=None):
    print("send serverchan message")
    resource = sc_send(sendkey, title, desp, options)
    return resource


def send_telegram_bot():
    print("send telegram_bot message")
    pass


async def send_log(user: UserInfo, message: any):
    channel = user.run_notice_ids
    if channel & ChannelType.TelegramBot:
        print("channel:TelegramBot")
        # context: ContextTypes.DEFAULT_TYPE = message['context']
        # if context is not None:
        #     context.bot.send_message()

    if channel & ChannelType.Serverchan and user.has_serverchan():
        send_serverchan(user.serverchan_token, user.name + ' ' + message['title'], message['log'], {"tags": message['tags']})
    if channel & ChannelType.Serverchan3 and user.has_serverchan3():
        send_serverchan_3(user.serverchan3_token, user.name + ' ' + message['title'], message['log'], {"tags": message['tags']})

    logger.info(message['log'])

