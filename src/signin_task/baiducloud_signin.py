import datetime
import re
from typing import Any

import pytz
# from typing import re

import requests
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

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
        'Referer': 'https://pan.baidu.com/wap/svip/growth/task',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': cookie
    }
    return headers

def start_signin(cookie)-> list[Any]:
    url = 'https://pan.baidu.com/rest/2.0/membership/level?app_id=250528&web=5&method=signin'
    headers = get_header(cookie)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sign_point = re.search(r'points":(\d+)', response.text)
        signin_error_msg = re.search(r'"error_msg":"(.*?)"', response.text)
        success = True
        if sign_point:
            text = f"获得积分: {sign_point.group(1)}\n"
        else:
            text = signin_error_msg.group(1)
    else:
        success = False
        text = response.text
    return [success, text]

# 签到
def signin(user: UserInfo = None) -> list[Any]:
    day = utils.get_today_str()
    try:
        [success, text] = start_signin(user.baiducloud_cookie)
    except Exception as e:
        success = False
        text = str(e)
    if success:
        text = f"时间：{day} （UTC+8）\n结果：{text}"
    else:
        text = f"时间：{day} （UTC+8）\n结果：签到失败。\n原因：{text}"
    return [success, text]

# 获取答题信息
def get_answer(cookie) -> list[Any]:
    url = 'https://pan.baidu.com/act/v2/membergrowv2/getdailyquestion?app_id=250528&web=5'
    response = requests.get(url, headers=get_header(cookie))
    if response.status_code == 200:
        ans = re.search(r'"answer":(\d+)', response.text)
        ask_id = re.search(r'"ask_id":(\d+)', response.text)
        ques = re.search(r'"question":"(.*?)"', response.text)
        if ans and ask_id:
            return [ans.group(1), ask_id.group(1), ques.group(1)]
    return [None, None, None]

# 开始答题
def start_answer(ans, ask_id, cookie):
    url = f'https://pan.baidu.com/act/v2/membergrowv2/answerquestion?app_id=250528&web=5&ask_id={ask_id}&answer={ans}'
    response = requests.get(url, headers=get_header(cookie))
    if response.status_code == 200:
        answer_msg = re.search(r'"show_msg":"(.*?)"', response.text)
        answer_score = re.search(r'"score":(\d+)', response.text)
        success = True
        if answer_score:
            text = f"答题成功, 获得积分: {answer_score.group(1)}\n{answer_msg.group(1)}"
        else:
            text = f"{answer_msg.group(1)}"
    else:
        success = False
        text = response.text
    return [success, text]

def answer(user: UserInfo = None) -> list[Any]:
    day = utils.get_today_str()
    try:
        ans, ask_id, ques = get_answer(user.baiducloud_cookie)
        [success, text] = start_answer(ans, ask_id, user.baiducloud_cookie)
    except Exception as e:
        success = False
        ques = ""
        text = str(e)

    if success:
        text = f"时间: {day} （UTC+8）\n问题: {ques}\n答案: {ans}\n结果: {text}"
    else:
        text = f"时间: {day} （UTC+8）\n问题: {ques}\n答案: {ans}\n结果: 答题失败。\n原因: {text}"

    return [success, text]



def get_baiducloud_user_info(user: UserInfo = None) -> str:
    url = 'https://pan.baidu.com/rest/2.0/membership/user?app_id=250528&web=5&method=query'
    response = requests.get(url, headers=get_header(user.baiducloud_cookie))
    if response.status_code == 200:
        current_value = re.search(r'current_value":(\d+)', response.text)
        current_level = re.search(r'current_level":(\d+)', response.text)
        text = f"当前会员等级: {current_level.group(1) if current_level else '未知'}, 成长值: {current_value.group(1) if current_value else '未知'}"
    else:
        text = "获取用户信息失败!"
    return text


# 是否为baiducloud命令
def is_baiducloud_command(command_id: CommandType) -> bool:
    return (command_id == CommandType.NewBaiducloud or
            command_id == CommandType.DelBaiducloud)


def is_baiducloud_button(button: str) -> bool:
    return (button == "start_baiducloud" or button == "my_baiducloud" or button == "run_baiducloud_signin" or
            button == "run_baiducloud_answer" or button == "new_baiducloud_signin" or button == "get_baiducloud_info" or
            button == "del_baiducloud_signin")


async def task_baiducloud_signin(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> list[Any]:
    if user is None:
        return [False, "账号不存在"]

    if not user.has_baiducloud():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return [False, text]

    await context.bot.send_message(chat_id=user.id, text="baiducloud 正在签到...")
    [success, text] = signin(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )

    logger.info(text)
    return [success, text]


async def task_baiducloud_answer(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> list[Any]:
    if user is None:
        return [False, "账号不存在"]

    if not user.has_baiducloud():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return [False, text]

    await context.bot.send_message(chat_id=user.id, text="baiducloud 正在答题...")
    [success, text] = answer(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )

    logger.info(text)
    return [success, text]

async def task_baiducloud_user_info(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> str:
    if user is None:
        return "账号不存在"
    if not user.has_baiducloud():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return text
    await context.bot.send_message(chat_id=user.id, text="baiducloud 正在查询会员信息...")
    text = get_baiducloud_user_info(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )
    logger.info(text)
    return text

class BaiduCloudSignin:
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
        job_queue.run_daily(self.baiducloud_signin_task, self.signin_time)  # baiducloud自动签到
        # job_queue.run_once(self.baiducloud_signin_task, 3)

    async def show_start_baiducloud(self, update: Update, context: CallbackContext):
        user = self.bot.get_user_by_update(update)
        logger.info("show_start_baiducloud")
        await keyboard_button.edit_keyboard(self.bot, update, context, 'start_baiducloud')
        user.command_state = CommandType.Empty

    # 新账号
    async def command_new_baiducloud(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if user.has_baiducloud():
            text = f"你当前已经有一个签到账号：\n{user.baiducloud_cookie}\n你可以回复新的cookie，这将会覆盖旧的cookie"
        else:
            text = "请回复你baiducloud签到的cookie"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_new_baiducloud reply:" + text)
        user.command_state = CommandType.NewBaiducloud


    # 查看我的账号信息
    async def command_my_baiducloud(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = ""
        # #1
        ss = f"您当前百度云账号信息：\n"
        text += ss
        await context.bot.send_message(chat_id=user.id, text=ss)

        has_baidu = False
        # #2
        if user.has_baiducloud():
            ss = f"你有一个账号：\n{user.baiducloud_cookie}\n"
            text += ss
            await context.bot.send_message(chat_id=user.id, text=ss)
            has_baidu = True

        if not has_baidu:
            ss = f"你当前没有账号\n"
            text += ss
            await context.bot.send_message(chat_id=user.id, text=ss)
        else:
            # #4
            if user.has_run_task(CommandType.NewBaiducloud):
                ss = f"签到任务已启用，开始时间：{self.signin_time}"
                text += ss
                await context.bot.send_message(chat_id=user.id, text=ss)

        logger.info("command_my_baiducloud reply:" + text)
        user.command_state = CommandType.Empty


    async def command_get_baiducloud_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = await task_baiducloud_user_info(user, context)
        message = {
            'title': "baiducloud信息查询",
            'tags': "baiducloud_signin",
            'log': text
        }
        await utils.send_log(user, message)
        user.command_state = CommandType.Empty

    async def command_run_baiducloud_signin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        [success, text] = await task_baiducloud_signin(user, context)
        self.last_signin = text
        message = {
            'title': "baiducloud签到-" + ("成功" if success else "失败"),
            'tags': "baiducloud_signin",
            'log': text
        }
        await utils.send_log(user, message)
        user.command_state = CommandType.Empty

    async def command_run_baiducloud_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        [success, text] = await task_baiducloud_answer(user, context)
        self.last_signin = text
        message = {
            'title': "baiducloud答题-" + ("成功" if success else "失败"),
            'tags': "baiducloud_signin",
            'log': text
        }
        await utils.send_log(user, message)
        user.command_state = CommandType.Empty

    # 删除账号
    async def command_del_baiducloud(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_baiducloud():
            command_state = CommandType.Empty
            text = f"你当前没有账号\n"
        else:
            command_state = CommandType.DelBaiducloud
            text = "请回复yes确认删除数据"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_del_baiducloud reply:" + text)
        user.command_state = command_state


    # 命令回复
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = update.message.text
        command_state = user.command_state

        if command_state == CommandType.NewBaiducloud:
            user.baiducloud_cookie = text
            text = f"账号添加成功:\n"
            await context.bot.send_message(chat_id=user.id, text=text)
            user.add_run_task(CommandType.NewBaiducloud)
            self.bot.save_user(True)

        if command_state == CommandType.DelBaiducloud:
            if text == "yes":
                self.last_signin = ""
                self.notice_user = []

                user.del_run_task(CommandType.NewBaiducloud)
                text = f"账号删除成功！"
                await context.bot.send_message(chat_id=user.id, text=text)
                text += f"\n\n已删除账号：\n{user.baiducloud_cookie}"
                user.baiducloud_cookie = ""
                self.bot.save_user()

        logger.info("on_text reply:" + text)
        user.command_state = CommandType.Empty

    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, button_name: str):
        user = self.bot.get_user_by_update(update)

        if button_name == "start_baiducloud":
            await self.show_start_baiducloud(update, context)
        elif button_name == "my_baiducloud":
            await self.command_my_baiducloud(update, context)
        elif button_name == "get_baiducloud_info":
            await self.command_get_baiducloud_info(update, context)
        elif button_name == "run_baiducloud_signin":
            await self.command_run_baiducloud_signin(update, context)
        elif button_name == "run_baiducloud_answer":
            await self.command_run_baiducloud_answer(update, context)
        elif button_name == "new_baiducloud_signin":
            await self.command_new_baiducloud(update, context)
        elif button_name == "del_baiducloud_signin":
            await self.command_del_baiducloud(update, context)
        else:
            user.command_state = CommandType.Empty

    # 定时自动签到任务
    async def baiducloud_signin_task(self, context: ContextTypes.DEFAULT_TYPE):
        current_datetime = utils.get_today_str()
        print("baiducloud_signin_task:" + str(current_datetime))

        if self.bot.user_dict is not None:
            for user_id, user in self.bot.user_dict.items():
                is_notice = False
                if not user.has_run_task(CommandType.NewBaiducloud):
                    signin_success = False
                    answer_success = False
                    signin_text = "baiducloud自动签到任务没有运行中!"
                    answer_text = ""
                    vip_info_text = ""
                    if user_id not in self.notice_user:
                        self.notice_user.append(user_id)
                        await context.bot.send_message(chat_id=user.id, text=signin_text)
                        is_notice = True
                else:
                    # 自动签到
                    [signin_success, signin_text] = await task_baiducloud_signin(user, context)
                    [answer_success, answer_text] = await task_baiducloud_answer(user, context)
                    vip_info_text = await task_baiducloud_user_info(user, context)
                    self.last_signin = f"{signin_text}\n\n{answer_text}"
                    is_notice = True

                if is_notice:
                    message = {
                        'title': "baiducloud签到-" + ("成功" if signin_success else "失败"),
                        'tags': "baiducloud_signin",
                        'log': signin_text
                    }
                    await utils.send_log(user, message)

                    message = {
                        'title': "baiducloud答题-" + ("成功" if answer_success else "失败"),
                        'tags': "baiducloud_signin",
                        'log': answer_text
                    }
                    await utils.send_log(user, message)

                    message = {
                        'title': "baiducloud会员信息查询",
                        'tags': "baiducloud_signin",
                        'log': vip_info_text
                    }
                    await utils.send_log(user, message)
