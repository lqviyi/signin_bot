import datetime
import json
from typing import Any

import pytz
import requests
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from main import logger
from src import utils
from src.configs import config, keyboard_button
from src.configs.command_type import CommandType
from src.configs.user_info import UserInfo



# @property
def start(cookie):
    proxies = {
        "http": config.common['gladosProxyHttp'],
        "https": config.common['gladosProxyHttps']
    }
    # 创建一个session,作用会自动保存cookie
    session = requests.session()
    # 点签到之后的页
    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"
    referer = 'https://glados.rocks/console/checkin'
    # checkin = requests.post(url,headers={'cookie': cookie ,'referer': referer })
    # state =  requests.get(url2,headers={'cookie': cookie ,'referer': referer})
    origin = "https://glados.rocks"
    useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    # 请求负载
    payload = {
        # 'token': 'glados_network'
        'token': 'glados.one'
        # 'token': 'glados.network'
    }
    # referer 当浏览器向web服务器发送请求的时候，一般会带上Referer，告诉服务器我是从哪个页面链接过来的，服务器 籍此可以获得一些信息用于处理。
    # json.dumps请求序列化
    checkin = session.post(url
                           ,
                           headers={'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent,
                                    'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload),
                           proxies=proxies)
    state = session.get(url2,
                        headers={'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent},
                        proxies=proxies)
    # print(res)
    # print(checkin.text )
    if 'message' in checkin.text:
        mess = checkin.json()['message']
        _time = state.json()['data']['leftDays']
        _time = _time.split('.')[0]
        # print(time)
        text = mess + '，you have ' + _time + ' days left'
        # print(text)
        return text


# 签到后调用tg_bot回复结果
# @property
def signin(user: UserInfo) -> list[Any]:
    # return [True, "签到测试"]
    success = True
    day = utils.get_today_str()
    try:
        text = start(user.glados_cookie)
    except Exception as e:
        success = False
        text = str(e)
    if success:
        text = f"时间：{day} （UTC+8）\n结果：{text}"
    else:
        text = f"时间：{day} （UTC+8）\n结果：签到失败。\n原因：{text}"

    return [success, text]


# 是否为glados命令
def is_glados_command(command_id: CommandType) -> bool:
    return (command_id == CommandType.NewGlados
            or command_id == CommandType.DelGlados)


def is_glados_button(button: str) -> bool:
    return (button == "start_glados" or button == "my_glados" or button == "new_glados" or
            button == "run_glados" or button == "enable_glados" or button == "disable_glados" or
            button == "del_glados")


async def task_glados_signin(user: UserInfo, context: ContextTypes.DEFAULT_TYPE) -> list[Any]:
    if user is None:
        return [False, "账号不存在"]

    if not user.has_glados():
        text = f"你当前没有账号\n"
        await context.bot.send_message(chat_id=user.id, text=text)
        return [False, text]

    await context.bot.send_message(chat_id=user.id, text="glados 正在签到...")
    [success, text] = signin(user)
    await context.bot.send_message(
        chat_id=user.id,
        text=text
    )

    logger.info(text)
    return [success, text]


class GladosSignin:

    def __init__(self, bot):
        self.bot = bot
        self.last_signin = ""
        self.notice_user = []  # 没有开通自动签到的提示

        self.signin_time = datetime.time(2, 0, 0, 0, pytz.timezone('Asia/Shanghai'))
        self.add_handler()
        self.add_auto_task()

    def add_handler(self):
        if self.bot is None:
            return False

    def add_auto_task(self):
        job_queue = self.bot.application.job_queue
        job_queue.run_daily(self.glados_signin_task, self.signin_time)  # glados自动签到
        # job_queue.run_once(self.glados_signin_task, 3)

    async def show_start_glados(self, update: Update, context: CallbackContext):
        user = self.bot.get_user_by_update(update)
        logger.info("show_start_glados")
        await keyboard_button.edit_keyboard(self.bot, update, context, 'start_glados')
        user.command_state = CommandType.Empty

    # glados新账号
    async def command_new_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if user.has_glados():
            text = f"你当前已经有一个账号：\n{user.glados_cookie}\n你可以回复新的cookie，这将会覆盖旧的cookie"
        else:
            text = "请回复你glados签到的cookie"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_new_glados reply:" + text)
        user.command_state = CommandType.NewGlados

    # 主动调用签到
    async def command_run_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        [success, text] = await task_glados_signin(user, context)
        self.last_signin = text
        user.command_state = CommandType.Empty
        message = {
            'title': "glados签到-" + ("成功" if success else "失败"),
            'tags': "glados_signin",
            'log': text
        }
        await utils.send_log(user, message)

    # 查看我的账号信息
    async def command_my_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = ""
        # #1
        ss = f"您当前glados账号信息：\n"
        text += ss
        await context.bot.send_message(chat_id=user.id, text=ss)

        has_glados = False
        # #2
        if user.has_glados():
            ss = f"你有一个账号：\n{user.glados_cookie}\n"
            has_glados = True
        else:
            ss = f"你当前没有账号!\n"
        text += ss
        await context.bot.send_message(chat_id=user.id, text=ss)

        if has_glados:
            # #3
            if self.last_signin:
                ss = f"上一次签到结果：\n{self.last_signin}\n"
                text += ss
                await context.bot.send_message(chat_id=user.id, text=ss)

            # #4
            if user.has_run_task(CommandType.NewGlados):
                ss = f"已开启自动签到，自动签到时间：{self.signin_time}\n"
            else:
                ss = f"未开启自动签到!\n"
            text += ss
            await context.bot.send_message(chat_id=user.id, text=ss)

        logger.info("command_my_glados reply:" + text)
        user.command_state = CommandType.Empty

    # 删除账号
    async def command_del_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_glados():
            command_state = CommandType.Empty
            text = f"你当前没有账号!"
        else:
            command_state = CommandType.DelGlados
            text = "请回复yes确认删除数据!"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_del_glados reply:" + text)
        user.command_state = command_state

    # 开启自动任务
    async def command_enable_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE, save=True):
        user = self.bot.get_user_by_update(update)

        if not user.has_glados():
            text = f"你当前没有账号!"
        else:
            user.add_run_task(CommandType.NewGlados)
            if save:
                self.bot.save_user()
            text = "已开启自动签到任务!"

        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_enable_glados reply:" + text)
        user.command_state = CommandType.Empty

    # 关闭自动任务
    async def command_disable_glados(self, update: Update, context: ContextTypes.DEFAULT_TYPE, save=True):
        user = self.bot.get_user_by_update(update)

        if not user.has_glados():
            text = f"你当前没有账号!"
        else:
            text = "已关闭自动签到任务!"
            user.del_run_task(CommandType.NewGlados)
            if save:
                self.bot.save_user()

        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_disable_glados reply:" + text)
        user.command_state = CommandType.Empty

    # 命令回复
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = update.message.text
        command_state = user.command_state

        if command_state == CommandType.NewGlados:
            user.glados_cookie = text
            text = f"账号添加成功!"
            await context.bot.send_message(chat_id=user.id, text=text)
            await self.command_enable_glados(update, context, False)
            self.bot.save_user(True)

        if command_state == CommandType.DelGlados:
            if text == "yes":
                self.last_signin = ""
                self.notice_user = []

                await self.command_disable_glados(update, context, False)
                text = f"账号删除成功!"
                await context.bot.send_message(chat_id=user.id, text=text)
                text += f"\n\n已删除账号：\n{user.glados_cookie}"
                user.glados_cookie = ""
                self.bot.save_user()

        logger.info("on_text reply:" + text)
        user.command_state = CommandType.Empty

    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, button_name: str):
        user = self.bot.get_user_by_update(update)

        if button_name == "start_glados":
            await self.show_start_glados(update, context)
        elif button_name == "my_glados":
            await self.command_my_glados(update, context)
        elif button_name == "new_glados":
            await self.command_new_glados(update, context)
        elif button_name == "run_glados":
            await self.command_run_glados(update, context)
        elif button_name == "enable_glados":
            await self.command_enable_glados(update, context)
        elif button_name == "disable_glados":
            await self.command_disable_glados(update, context)
        elif button_name == "del_glados":
            await self.command_del_glados(update, context)
        else:
            user.command_state = CommandType.Empty

    # 定时自动签到任务
    async def glados_signin_task(self, context: ContextTypes.DEFAULT_TYPE):
        current_datetime = utils.get_today_str()
        print("glados_signin_task:" + str(current_datetime))

        if self.bot.user_dict is not None:
            for user_id, user in self.bot.user_dict.items():
                is_notice = False
                if not user.has_run_task(CommandType.NewGlados):
                    success = False
                    text = "glados自动签到任务没有运行中!"
                    if user_id not in self.notice_user:
                        self.notice_user.append(user_id)
                        await context.bot.send_message(chat_id=user.id, text=text)
                        is_notice = True
                else:
                    # 自动签到
                    [success, text] = await task_glados_signin(user, context)
                    is_notice = True
                    self.last_signin = text

                if is_notice:
                    message = {
                        'title': "glados签到-" + ("成功" if success else "失败"),
                        'tags': "glados_signin",
                        'log': text
                    }
                    await utils.send_log(user, message)
