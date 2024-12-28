from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from main import logger
from src.configs.command_type import CommandType

keyboard_list = {
    'my': {
        'title': '请选择你要查看的账号:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Glados", callback_data="my_glados"),
                    InlineKeyboardButton("百度网盘", callback_data="my_baiducloud"),
                ],
                [
                    InlineKeyboardButton("Server酱", callback_data="my_serverchan"),
                    InlineKeyboardButton("Server酱3", callback_data="my_serverchan3"),
                ],
            ]
        )
    },
    'task': {
        'title': '你可以选择以下任务:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Glados签到", callback_data="start_glados"),
                    InlineKeyboardButton("百度网盘签到", callback_data="start_baiducloud"),
                    # InlineKeyboardButton("阿里云盘签到", callback_data="start_aliyundrive"),
                ],
                [
                    InlineKeyboardButton("close keyboard button", callback_data="close"),
                ]
            ]
        )
    },
    'notice': {
        'title': '你可以选择以下新增的通知渠道:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Server酱通知", callback_data="serverchan"),
                    InlineKeyboardButton("Server酱3通知", callback_data="serverchan3"),
                ],
                [
                    InlineKeyboardButton("close keyboard button", callback_data="close"),
                ],
            ]
        )
    },
    'delete': {
        'title': '请选择你要删除的账号:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Glados", callback_data="del_glados"),
                    InlineKeyboardButton("百度网盘", callback_data="del_baiducloud_signin"),
                ],
                [
                    InlineKeyboardButton("Server酱", callback_data="del_serverchan"),
                    InlineKeyboardButton("Server酱3", callback_data="del_serverchan3"),
                ],
                [
                    InlineKeyboardButton("删除所有账号数据", callback_data="delete"),
                ],
            ]
        )
    },
    'start_glados': {
        'title': '请选择你要处理glados任务的命令:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("当前账号", callback_data="my_glados"),
                    InlineKeyboardButton("新建账号", callback_data="new_glados"),
                    InlineKeyboardButton("删除账号", callback_data="del_glados"),
                ],
                [
                    InlineKeyboardButton("立即签到", callback_data="run_glados"),
                    InlineKeyboardButton("开启自动签到", callback_data="enable_glados"),
                    InlineKeyboardButton("关闭自动签到", callback_data="disable_glados"),
                ],
                [
                    InlineKeyboardButton("<< 返回任务菜单", callback_data="task")
                ],
            ]
        )
    },
    'start_baiducloud': {
        'title': '请选择你要处理百度网盘任务的命令:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("当前账号", callback_data="my_baiducloud"),
                    InlineKeyboardButton("新建账号", callback_data="new_baiducloud_signin"),
                    InlineKeyboardButton("删除账号", callback_data="del_baiducloud_signin"),
                ],
                [
                    InlineKeyboardButton("会员信息", callback_data="get_baiducloud_info"),
                    InlineKeyboardButton("立即签到", callback_data="run_baiducloud_signin"),
                    InlineKeyboardButton("立即答题", callback_data="run_baiducloud_answer"),
                ],
                [
                    InlineKeyboardButton("<< 返回任务菜单", callback_data="task")
                ],
            ]
        )
    },
    'start_aliyundrive': {
        'title': '请选择你要处理阿里云盘任务的命令:',
        'reply_markup': InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("当前账号", callback_data="my_aliyundrive"),
                    InlineKeyboardButton("新建账号", callback_data="new_aliyundrive"),
                    InlineKeyboardButton("删除账号", callback_data="del_aliyundrive"),
                ],
                [
                    InlineKeyboardButton("立即签到", callback_data="run_aliyundrive")
                ],
                [
                    InlineKeyboardButton("<< 返回任务菜单", callback_data="task")
                ],
            ]
        )
    },
}


# 修改并返回新keyboard
async def edit_keyboard(bot, update: Update, context: ContextTypes.DEFAULT_TYPE, keyboard_name: str):
    query = update.callback_query
    user = bot.get_user(query.from_user.id, query.from_user.name)
    keyboard = keyboard_list[keyboard_name]
    await query.edit_message_text(keyboard['title'], reply_markup=keyboard['reply_markup'])
    logger.info("edit_keyboard: " + keyboard_name)
    user.command_state = CommandType.Empty


# 回复新keyboard
async def reply_keyboard(bot, update: Update, context: ContextTypes.DEFAULT_TYPE, keyboard_name: str):
    user = bot.get_user(update.message.from_user.id, update.message.from_user.name)
    keyboard = keyboard_list[keyboard_name]
    await update.message.reply_text(keyboard['title'], reply_markup=keyboard['reply_markup'])
    logger.info("reply_keyboard: " + keyboard_name)
    user.command_state = CommandType.Empty
