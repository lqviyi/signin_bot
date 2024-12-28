from dataclasses import dataclass, asdict
from typing import Dict, Any

from src.configs.channel_type import ChannelType
from src.configs.command_type import CommandType


@dataclass
class UserInfo:
    id: int = 0
    name: str = ""
    glados_cookie: str = ""
    baiducloud_cookie: str = ""
    serverchan_token: str = ""
    serverchan3_token: str = ""
    # is_valid: bool = True
    run_task_ids: list[int] = None
    run_notice_ids: ChannelType = ChannelType.Empty
    command_state: CommandType = 0

    def add_run_task(self, task_id: CommandType):
        if self.run_task_ids is None:
            self.run_task_ids = []
        if task_id not in self.run_task_ids:
            self.run_task_ids.append(task_id)
    def del_run_task(self, task_id: CommandType):
        if self.run_task_ids is not None and task_id in self.run_task_ids:
            self.run_task_ids.remove(task_id)
    def has_run_task(self, task_id: CommandType) -> bool:
        return self.run_task_ids is not None and task_id in self.run_task_ids


    def add_run_notice(self, notice_id: ChannelType):
        self.run_notice_ids = self.run_notice_ids | notice_id

    def del_run_notice(self, notice_id: ChannelType):
        self.run_notice_ids = self.run_notice_ids & ~notice_id

    def has_run_notice(self, notice_id: ChannelType) -> bool:
        return self.run_notice_ids & notice_id > 0



    def has_glados(self) -> bool:
        return self.glados_cookie is not None and self.glados_cookie != ""

    def has_baiducloud(self) -> bool:
        return self.baiducloud_cookie is not None and self.baiducloud_cookie != ""


    def has_serverchan(self) -> bool:
        return self.serverchan_token is not None and self.serverchan_token != ""

    def has_serverchan3(self) -> bool:
        return self.serverchan3_token is not None and self.serverchan3_token != ""





    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UserInfo":
        return cls(**d)
