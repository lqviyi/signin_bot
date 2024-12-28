import json
import datetime
from os.path import isfile

import schedule
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, \
    MessageHandler, filters, CallbackQueryHandler

from src import utils, my_notice, admin_notice, my_log
from src.configs import config, keyboard_button
from src.configs.command_type import CommandType
from src.signin_task import glados_signin, baiducloud_signin
from src.signin_task.baiducloud_signin import BaiduCloudSignin
from src.signin_task.glados_signin import GladosSignin
from src.configs.user_info import UserInfo
from src.my_notice import MyNotice

logger = my_log.logger
common = config.common

class MyBot:
    need_save_user: bool = False

    def __init__(self, token):
        self.glados: GladosSignin = None
        self.baiducloud: BaiduCloudSignin = None
        self.m_notice: MyNotice = None
        self.token = token
        self.proxy = common['botProxy']
        self.user_dict = {}
        self.command_args = None

        # 加载本地缓存数据
        self.load()

        # build telegram bot
        self.application = (ApplicationBuilder().token(self.token)
                            .proxy(self.proxy)
                            .get_updates_proxy(self.proxy)
                            .read_timeout(7)
                            .get_updates_read_timeout(42)
                            .build())

        # 添加定时任务
        job_queue = self.application.job_queue
        # schedule.every().day.at("00:02").do(self.schedule_task)
        job_queue.run_repeating(self.minute_loop, interval=60, first=1)
        job_queue.run_daily(self.update_log_file, datetime.time(0, 2, 0, 0))  # glados自动签到
        job_queue.run_once(self.once_task_test, 3)

        """
        bot commands:
            start-开始测试
            my-查看我的账号
            task-查看任务
            notice-查看通知渠道
            delete-删除账号
        """
        # 监听命令处理
        start_handler = CommandHandler('start', self.command_start)
        my_handler = CommandHandler('my', self.command_my)
        delete_handler = CommandHandler('delete', self.command_delete)
        task_handler = CommandHandler('task', self.command_task)
        notice_handler = CommandHandler('notice', self.command_notice)
        text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.on_text)
        self.application.add_handler(start_handler)
        self.application.add_handler(my_handler)
        self.application.add_handler(delete_handler)
        self.application.add_handler(task_handler)
        self.application.add_handler(notice_handler)
        self.application.add_handler(text_handler)

        button_handler = CallbackQueryHandler(self.on_button)
        self.application.add_handler(button_handler)
        # 监听任务和通知处理
        self.add_other_handler()

        # Other handlers
        unknown_handler = MessageHandler(filters.COMMAND, self.command_unknown)
        self.application.add_handler(unknown_handler)

        # ...and the error handler
        self.application.add_error_handler(admin_notice.error_handler)

        self.application.run_polling()

    def add_other_handler(self):
        self.glados = GladosSignin(self)
        self.baiducloud = BaiduCloudSignin(self)
        self.m_notice = MyNotice(self)

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        text = "I'm a bot, please talk to me!"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("command_start reply:" + text)
        user.command_state = CommandType.Start

    async def command_my(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("command_my reply")
        await keyboard_button.reply_keyboard(self, update, context, 'my')
        user.command_state = CommandType.My

    async def command_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("command_my reply")
        await keyboard_button.reply_keyboard(self, update, context, 'delete')
        user.command_state = CommandType.Empty

    async def command_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("command_task reply")
        await keyboard_button.reply_keyboard(self, update, context, 'task')
        user.command_state = CommandType.Task

    async def command_notice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("command_add_notice reply")
        await keyboard_button.reply_keyboard(self, update, context, 'notice')
        user.command_state = CommandType.Notice

    async def command_unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        await context.bot.send_message(chat_id=user.id,
                                       text="Sorry, I didn't understand that command.")
        user.command_state = CommandType.Unknown



    async def show_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("show_task")
        await keyboard_button.edit_keyboard(self, update, context, 'task')
        user.command_state = CommandType.Empty

    async def button_delete_all_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        text = "请回复yes确认删除全部数据"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("button_delete_all_data reply:" + text)
        user.command_state = CommandType.Delete

    async def show_notice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        logger.info("show_notice")
        await keyboard_button.edit_keyboard(self, update, context, 'notice')
        user.command_state = CommandType.Empty



    # 回复处理
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.get_user_by_update(update)
        text = update.message.text

        logger.info("on_text:" + text)

        command_state = user.command_state

        # 注册新glados账号
        if self.glados is not None and glados_signin.is_glados_command(command_state):
            await self.glados.on_text(update, context)
            return

        # 注册新百度云账号
        if self.baiducloud is not None and baiducloud_signin.is_baiducloud_command(command_state):
            await self.baiducloud.on_text(update, context)
            return

        # 添加通知账号
        if self.m_notice is not None and my_notice.is_notice_command(command_state):
            await self.m_notice.on_text(update, context)
            return

        # 删除账号
        if command_state == CommandType.Delete:
            if text == "yes":
                self.user_dict.pop(user.id, None)
                self.save_user()
                await context.bot.send_message(chat_id=user.id, text=f"账号删除成功！")
                return

        await context.bot.send_message(chat_id=user.id, text=f"未知消息:{text}")
        user.command_state = CommandType.Empty


    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        user = self.get_user(query.from_user.id, query.from_user.name)

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        if query.data == "task":
            await self.show_task(update, context)
        elif query.data == "delete":
            await self.button_delete_all_data(update, context)
        elif query.data == "close":
            await query.edit_message_text(text=f"closed keyboard button")
        elif my_notice.is_notice_button(query.data):
            await self.m_notice.on_button(update, context, query.data)
        elif glados_signin.is_glados_button(query.data):
            await self.glados.on_button(update, context, query.data)
        elif baiducloud_signin.is_baiducloud_button(query.data):
            await self.baiducloud.on_button(update, context, query.data)
        else:
            await query.edit_message_text(text=f"Selected option: {query.data}")
            user.command_state = CommandType.Empty
        logger.info(f"on_button:" + query.data)



    def get_user(self, user_id: int, update_name: str = None) -> UserInfo:
        user = self.user_dict.get(user_id)
        new_user = False
        if user is None:
            user = UserInfo(id=user_id)
            self.user_dict[user_id] = user
            new_user = True
        if update_name is not None:
            user.name = update_name
        if new_user:
            self.save_user(user)
        return user

    def get_user_by_update(self, update: Update):
        if update and update.message and update.message.from_user:
            return self.get_user(update.message.from_user.id, update.message.from_user.name)
        if update and update.callback_query and update.callback_query.from_user:
            return self.get_user(update.callback_query.from_user.id, update.callback_query.from_user.name)
        return self.get_user(1)

    # 加载文件中保存的数据
    def load(self):
        user_list = []
        if isfile(r"./user_info.json"):
            with open("./user_info.json", 'r', encoding='utf-8') as f:
                user_list = json.loads(f.read())
        for user in user_list:
            if user['id'] is not None:
                user_obj = UserInfo.from_dict(user)
                self.user_dict[user_obj.id] = user_obj
        self.save_user(True)

    # 将新的数据保存
    def save_user(self, force=False):
        # 不立即保存，等定时自动保存
        if not force:
            self.need_save_user = True
            return
        if self.user_dict is not None:
            user_list = list(value.to_dict() for value in self.user_dict.values())
            try:
                with open(r"./user_info.json", 'w', encoding='utf-8') as file:
                    json.dump(user_list, file, ensure_ascii=False, indent=4)
                logger.info("save_user")
            except Exception as e:
                logger.error(e)
        self.need_save_user = False

    async def minute_loop(self, context: ContextTypes.DEFAULT_TYPE):
        logger.info("minute_loop:" + str(utils.get_nowtime()))

        if self.need_save_user:
            self.need_save_user = False
            self.save_user(force=True)
        # 执行定期schedule任务
        schedule.run_pending()

    # schedule的定时任务
    # async def schedule_task(self):
    #     logger.info("schedule_task：" + str(utils.get_nowtime()))

    async def update_log_file(self, context: ContextTypes.DEFAULT_TYPE):
        logger.info("update_log_file：" + str(utils.get_nowtime()))
        my_log.use_new_log()

    async def once_task_test(self, context: ContextTypes.DEFAULT_TYPE):
        logger.info("once_task_test:" + str(utils.get_nowtime()))
        # await self.glados_signin_task(context)
        # aliyundrive_signin.test_aliyun()


def run():
    MyBot(common['botToken'])


if __name__ == '__main__':
    run()
