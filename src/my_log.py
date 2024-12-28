import logging
from datetime import datetime, timedelta
import os

# 获取当前日期的字符串表示
today = datetime.today().strftime('%Y-%m-%d')

# logging.getLogger('httpx').setLevel(logging.WARNING)
# logging.getLogger('httpcore').setLevel(logging.WARNING)

# 创建一个日志记录器
logger = logging.getLogger('daily_logger')
# logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建一个处理器，用于写入当天的日志文件
# 注意：这里我们实际上没有使用TimedRotatingFileHandler的滚动功能
# 而是手动创建了一个包含日期的文件名
file_handler = logging.FileHandler(f'./logs/daily_log_{today}.log')

# 创建一个日志格式器，并设置其格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将处理器添加到日志记录器中
logger.addHandler(file_handler)

# 记录一些日志以测试配置
# logger.debug('这是一个调试信息')
# logger.info('这是一个信息')

# ...（其他日志记录操作）

# 在实际应用中，下面的代码不应该出现在这里
# 而应该由一个外部调度程序（如cron作业）每天运行一次
# 来创建新的FileHandler并添加到logger中，同时移除旧的FileHandler
# 下面的代码只是为了演示如何手动更改日志文件名
# 警告：这将导致日志丢失，因为旧的FileHandler被关闭了
# 在生产环境中，你应该确保旧的日志被适当地保存或归档


handler_list = [file_handler]

def use_new_log():
    # 假设现在是下一天，我们想要创建一个新的日志文件
    # 首先，关闭并移除旧的FileHandler

    for handler in handler_list:
        logger.removeHandler(handler)
        handler.close()

    handler_list.clear()

    # 获取新日期的字符串表示
    new_day = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')  # 这里只是为了模拟，实际上应该是下一天的日期

    # 创建一个新的FileHandler，指向新日期的日志文件
    new_file_handler = logging.FileHandler(f'daily_log_{new_day}.log')
    new_file_handler.setFormatter(formatter)

    # 将新的FileHandler添加到日志记录器中
    logger.addHandler(new_file_handler)

    handler_list.append(new_file_handler)

    # 记录一些新的日志以测试新配置（在实际应用中，这部分代码不应该出现在这里）
    logger.info('这是一个新日志文件的测试信息')