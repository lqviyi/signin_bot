import datetime
import json
import re
from typing import Any

import pytz
# from typing import re

import requests
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from http.cookies import SimpleCookie

from src import utils
from src.configs import keyboard_button
from src.configs.command_type import CommandType
from src.configs.user_info import UserInfo
from src.my_log import logger



def get_header(cookie) -> Any:
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'netdisk;12.10.2;2109119BC;android-android;13;JSbridge4.4.0;jointBridge;1.1.0;',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-platform': "Android",
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://big.bilibili.com/mobile/index',
        'Origin': 'https://big.bilibili.com/mobile/index',
        'Cookie': cookie
    }
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    return headers

def get_csrf(cookie) -> str:
    ck = SimpleCookie()
    ck.load(cookie)
    # 转为字典
    cookie_dict = {key: morsel.value for key, morsel in ck.items()}
    return cookie_dict.get('bili_jct', "")


def start_signin(cookie)-> list[Any]:
    url = 'https://api.bilibili.com/pgc/activity/score/task/sign2?'
    condition_dict = {
        'csrf': get_csrf(cookie),
    }

    for key in condition_dict:
        url += key + '=' + condition_dict[key] + '&'

    headers = get_header(cookie)
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        try:
            data = json.loads(response.text)

            # 安全提取，提供默认值（防止 key 不存在）
            code = data.get("code", 0)
            message = data.get("message", "")
            text = f"code: {code}\nmessage: {message}"
            success = False
            if code == 0:
                success = True
        except json.JSONDecodeError as e:
            text = "❌ 不是合法 JSON:\n" + response.text
            success = False
    else:
        success = False
        text = response.text
    return [success, text]


# 签到
def signin(user: UserInfo = None) -> list[Any]:
    day = utils.get_today_str()
    try:
        [success, text] = start_signin(user.bilibili_cookie)
    except Exception as e:
        success = False
        text = str(e)
    if success:
        text = f"时间：{day} （UTC+8）\n结果：{text}"
    else:
        text = f"时间：{day} （UTC+8）\n结果：签到失败。\n原因：{text}"
    return [success, text]


def get_bilibili_user_info(user: UserInfo = None) -> str:
    url = 'https://api.bilibili.com/x/vip/vip_center/sign_in/three_days_sign?'
    condition_dict = {
        'csrf': get_csrf(user.bilibili_cookie),
    }

    for key in condition_dict:
        url += key + '=' + condition_dict[key] + '&'

    response = requests.get(url, headers=get_header(user.bilibili_cookie))
    if response.status_code == 200:
        try:
            data = json.loads(response.text)

            # 安全提取，提供默认值（防止 key 不存在）
            point = data.get("data", {}).get("big_point", {}).get("point", 0)  # 默认 0
            signed = data.get("data", {}).get("three_day_sign", {}).get("signed", False)  # 默认 False
            code = data.get("code", 0)
            message = data.get("message", "")
            text = f"当前总积分: {point},  {'今日已签到' if signed else '今日未签到'} \ncode: {code}\nmessage: {message}"
        except json.JSONDecodeError as e:
            text = "❌ 不是合法 JSON:\n" + response.text
    else:
        text = "获取用户信息失败!"
    return text


# 是否为bilibili命令
def is_bilibili_command(command_id: CommandType) -> bool:
    return (command_id == CommandType.NewBilibili or
            command_id == CommandType.DelBilibili)

def is_bilibili_button(button: str) -> bool:
    return (button == "start_bilibili" or button == "my_bilibili" or button == "run_bilibili_signin" or
            button == "new_bilibili_signin" or button == "get_bilibili_info" or button == "del_bilibili_signin")


async def task_bilibili_signin(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> list[Any]:
    if user is None:
        return [False, "账号不存在"]

    if not user.has_bilibili():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return [False, text]

    await context.bot.send_message(chat_id=user.id, text="bilibili 正在签到...")
    [success, text] = signin(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )

    logger.info(text)
    return [success, text]


async def task_bilibili_user_info(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> str:
    if user is None:
        return "账号不存在"
    if not user.has_bilibili():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return text
    await context.bot.send_message(chat_id=user.id, text="bilibili 正在查询积分信息...")
    text = get_bilibili_user_info(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )
    logger.info(text)
    return text



class BilibiliSignin:
    def __init__(self, bot):
        self.bot = bot
        self.last_signin = ""
        self.notice_user = []  # 没有开通自动签到的提示

        self.signin_time = datetime.time(2, 10, 0, 0, pytz.timezone('Asia/Shanghai'))
        self.add_handler()
        self.add_auto_task()


    def add_handler(self):
        if self.bot is None:
            return False


    def add_auto_task(self):
        job_queue = self.bot.application.job_queue
        job_queue.run_daily(self.bilibili_signin_task, self.signin_time)  # bilibili自动签到
        job_queue.run_once(self.bilibili_signin_task, 3)

    async def show_start_bilibili(self, update: Update, context: CallbackContext):
        user = self.bot.get_user_by_update(update)
        logger.info("show_start_bilibili")
        await keyboard_button.edit_keyboard(self.bot, update, context, 'start_bilibili')
        user.command_state = CommandType.Empty

    # 新账号
    async def command_new_bilibili(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if user.has_bilibili():
            text = f"你当前已经有一个签到账号：\n{user.bilibili_cookie}\n你可以回复新的cookie，这将会覆盖旧的cookie"
        else:
            text = "请回复你bilibili签到的cookie"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_new_bilibili reply:" + text)
        user.command_state = CommandType.NewBilibili


    # 查看我的账号信息
    async def command_my_bilibili(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = ""
        # #1
        ss = f"您当前Bilibili账号信息：\n"
        text += ss
        await context.bot.send_message(chat_id=user.id, text=ss)

        has_bilibili = False
        # #2
        if user.has_bilibili():
            ss = f"你有一个账号：\n{user.bilibili_cookie}\n"
            text += ss
            await context.bot.send_message(chat_id=user.id, text=ss)
            has_bilibili = True

        if not has_bilibili:
            ss = f"你当前没有账号\n"
            text += ss
            await context.bot.send_message(chat_id=user.id, text=ss)
        else:
            # #4
            if user.has_run_task(CommandType.NewBilibili):
                ss = f"签到任务已启用，开始时间：{self.signin_time}"
                text += ss
                await context.bot.send_message(chat_id=user.id, text=ss)

        logger.info("command_my_bilibili reply:" + text)
        user.command_state = CommandType.Empty


    async def command_get_bilibili_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = await task_bilibili_user_info(user, context)
        message = {
            'title': "bilibili信息查询",
            'tags': "bilibili_signin",
            'log': text
        }
        await utils.send_log(user, message)
        user.command_state = CommandType.Empty

    async def command_run_bilibili_signin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        [success, text] = await task_bilibili_signin(user, context)
        # 签到成功后立即查询积分总量
        if success:
            await task_bilibili_user_info(user, context)
        self.last_signin = text
        message = {
            'title': "bilibili签到-" + ("成功" if success else "失败"),
            'tags': "bilibili_signin",
            'log': text
        }
        await utils.send_log(user, message)
        user.command_state = CommandType.Empty


    # 删除账号
    async def command_del_bilibili(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_bilibili():
            command_state = CommandType.Empty
            text = f"你当前没有账号\n"
        else:
            command_state = CommandType.DelBilibili
            text = "请回复yes确认删除数据"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_del_bilibili reply:" + text)
        user.command_state = command_state


    # 命令回复
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = update.message.text
        command_state = user.command_state

        if command_state == CommandType.NewBilibili:
            user.bilibili_cookie = text
            text = f"账号添加成功:\n"
            await context.bot.send_message(chat_id=user.id, text=text)
            user.add_run_task(CommandType.NewBilibili)
            self.bot.save_user(True)

        if command_state == CommandType.DelBilibili:
            if text == "yes":
                self.last_signin = ""
                self.notice_user = []

                user.del_run_task(CommandType.NewBilibili)
                text = f"账号删除成功！"
                await context.bot.send_message(chat_id=user.id, text=text)
                text += f"\n\n已删除账号：\n{user.bilibili_cookie}"
                user.bilibili_cookie = ""
                self.bot.save_user()

        logger.info("on_text reply:" + text)
        user.command_state = CommandType.Empty

    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, button_name: str):
        user = self.bot.get_user_by_update(update)

        if button_name == "start_bilibili":
            await self.show_start_bilibili(update, context)
        elif button_name == "my_bilibili":
            await self.command_my_bilibili(update, context)
        elif button_name == "get_bilibili_info":
            await self.command_get_bilibili_info(update, context)
        elif button_name == "run_bilibili_signin":
            await self.command_run_bilibili_signin(update, context)
        elif button_name == "new_bilibili_signin":
            await self.command_new_bilibili(update, context)
        elif button_name == "del_bilibili_signin":
            await self.command_del_bilibili(update, context)
        else:
            user.command_state = CommandType.Empty

    # 定时自动签到任务
    async def bilibili_signin_task(self, context: ContextTypes.DEFAULT_TYPE):
        current_datetime = utils.get_today_str()
        print("bilibili_signin_task:" + str(current_datetime))

        if self.bot.user_dict is not None:
            for user_id, user in self.bot.user_dict.items():
                is_notice = False
                if not user.has_run_task(CommandType.NewBilibili):
                    signin_success = False
                    signin_text = "bilibili自动签到任务没有运行中!"
                    vip_info_text = ""
                    if user_id not in self.notice_user:
                        self.notice_user.append(user_id)
                        await context.bot.send_message(chat_id=user.id, text=signin_text)
                        is_notice = True
                else:
                    # 自动签到
                    [signin_success, signin_text] = await task_bilibili_signin(user, context)
                    vip_info_text = await task_bilibili_user_info(user, context)
                    self.last_signin = f"{signin_text}\n"
                    is_notice = True

                if is_notice:
                    message = {
                        'title': "bilibili签到-" + ("成功" if signin_success else "失败"),
                        'tags': "bilibili_signin",
                        'log': signin_text
                    }
                    await utils.send_log(user, message)

                    message = {
                        'title': "bilibili积分查询",
                        'tags': "bilibili_signin",
                        'log': vip_info_text
                    }
                    await utils.send_log(user, message)
