import re
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

def parse_loose_cookie(cookie_str: str) -> dict:
    """
    解析宽松格式的 Cookie 字符串，支持 key 含 [] 等特殊字符
    """
    cookie_dict = {}
    # 匹配: key=value （key 可含字母、数字、下划线、中括号等；value 到 ; 或结尾）
    pattern = r'([^=;\s\0]+)=([^;]*?)(?=;\s*[^=;\s\0]+=|$)'
    for match in re.finditer(pattern, cookie_str):
        key = match.group(1).strip()
        value = match.group(2).strip()
        # 去掉可能的首尾引号
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        cookie_dict[key] = value
    return cookie_dict



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

