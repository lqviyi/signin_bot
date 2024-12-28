from telegram import Update
from telegram.ext import ContextTypes

from main import logger
from src.configs.channel_type import ChannelType
from src.configs.command_type import CommandType



def is_notice_command(command_id: CommandType) -> bool:
    return (command_id == CommandType.Serverchan or command_id == CommandType.Serverchan3 or
            command_id == CommandType.DelServerchan or command_id == CommandType.DelServerchan3)

def is_notice_button(button: str) -> bool:
    return (button == "serverchan" or button == "serverchan3" or button == "my_serverchan" or
            button == "my_serverchan3" or button == "del_serverchan" or
            button == "del_serverchan3")


class MyNotice:
    def __init__(self, bot):
        self.bot = bot

        # self.add_handler()

    def add_handler(self):
        if self.bot is None:
            return False

    async def button_serverchan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = "请回复你Server酱的sendkey"
        if user.has_serverchan():
            text = f"你当前已经有一个Server酱:\n{user.serverchan_token}\n回复新的sendkey将会覆盖旧的sendkey"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("button_serverchan reply:" + text)
        user.command_state = CommandType.Serverchan

    async def button_serverchan3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        text = "请回复你Server酱3的sendkey"
        if user.has_serverchan3():
            text = f"你当前已经有一个Server酱3:\n{user.serverchan3_token}\n回复新的sendkey将会覆盖旧的sendkey"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("button_serverchan3 reply:" + text)
        user.command_state = CommandType.Serverchan3

    async def button_my_serverchan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_serverchan():
            text = f"你当前没有Server酱账号!"
        else:
            text = f"你当前Server酱账号:\n{user.serverchan_token}"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("button_my_serverchan reply:" + text)
        user.command_state = CommandType.Empty

    async def button_my_serverchan3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_serverchan3():
            text = f"你当前没有Server酱3账号!"
        else:
            text = f"你当前Server酱3账号:\n{user.serverchan3_token}"
        await context.bot.send_message(chat_id=user.id, text=text)
        logger.info("button_my_serverchan3 reply:" + text)
        user.command_state = CommandType.Empty

    async def button_del_serverchan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_serverchan():
            command_state = CommandType.Empty
            text = f"你当前没有Server酱账号!"
        else:
            command_state = CommandType.DelServerchan
            text = "请回复yes确认删除Server酱账号!"
        await context.bot.send_message(chat_id=user.id, text=text)
        user.command_state = command_state


    async def button_del_serverchan3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user_by_update(update)
        if not user.has_serverchan3():
            command_state = CommandType.Empty
            text = f"你当前没有Server酱3账号!"
        else:
            command_state = CommandType.DelServerchan3
            text = "请回复yes确认删除Server酱3账号!"
        await context.bot.send_message(chat_id=user.id, text=text)
        user.command_state = command_state


    # 命令回复
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.bot.get_user(update.message.from_user.id, update.message.from_user.name)
        text = update.message.text
        command_state = user.command_state

        if command_state == CommandType.Serverchan:
            if user.serverchan_token != text:
                user.serverchan_token = text
                user.add_run_notice(ChannelType.Serverchan)
                self.bot.save_user(True)
            await context.bot.send_message(chat_id=user.id, text=f"Server酱 key添加成功:{text}")
            # await context.bot.send_message(chat_id=user.id,
            #                                text=f"任务结果将同步至Server酱\n 回复命令可取消通知 /disable_serverchan")

        if command_state == CommandType.Serverchan3:
            if user.serverchan3_token != text:
                user.serverchan3_token = text
                user.add_run_notice(ChannelType.Serverchan3)
                self.bot.save_user(True)
            await context.bot.send_message(chat_id=user.id, text=f"Server酱3 key添加成功:{text}")
            # await context.bot.send_message(chat_id=user.id,
            #                                text=f"任务结果将同步至Server酱3\n 回复命令可取消通知 /disable_serverchan")


        if command_state == CommandType.DelServerchan:
            if text == "yes":
                text = f"账号删除Server酱成功!"
                await context.bot.send_message(chat_id=user.id, text=text)
                text += f"\n\n已删除账号：\n{user.serverchan_token}"
                user.serverchan_token = ""
                self.bot.save_user()

        if command_state == CommandType.DelServerchan3:
            if text == "yes":
                text = f"账号删除Server酱成功!"
                await context.bot.send_message(chat_id=user.id, text=text)
                text += f"\n\n已删除账号：\n{user.serverchan3_token}"
                user.serverchan3_token = ""
                self.bot.save_user()

        logger.info("on_text reply:" + text)
        user.command_state = CommandType.Empty

    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, button_name: str):
        user = self.bot.get_user_by_update(update)

        if button_name == "serverchan":
            await self.button_serverchan(update, context)
        elif button_name == "serverchan3":
            await self.button_serverchan3(update, context)
        elif button_name == "my_serverchan":
            await self.button_my_serverchan(update, context)
        elif button_name == "my_serverchan3":
            await self.button_my_serverchan3(update, context)
        elif button_name == "del_serverchan":
            await self.button_del_serverchan(update, context)
        elif button_name == "del_serverchan3":
            await self.button_del_serverchan3(update, context)
        else:
            user.command_state = CommandType.Empty