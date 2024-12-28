from enum import IntEnum


class CommandType(IntEnum):
    Unknown = -1
    Empty = 0
    Start = 1
    My = 2
    Delete = 3
    Task = 4
    Notice = 5

    # 任务
    NewGlados = 400
    DelGlados = 401

    NewBaiducloud = 410
    DelBaiducloud = 411

    NewAliyundrive = 420
    DelAliyundrive = 421

    # 通知渠道
    Serverchan = 500
    Serverchan3 = 501
    DelServerchan = 502
    DelServerchan3 = 503