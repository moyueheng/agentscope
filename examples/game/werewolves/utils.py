# -*- coding: utf-8 -*-
"""狼人杀游戏的工具函数。"""

from typing import Any

import numpy as np

from prompt import Prompts

from agentscope.message import Msg
from agentscope.agent import ReActAgent, AgentBase

MAX_GAME_ROUND = 30
MAX_DISCUSSION_ROUND = 3  # 每个狼人最多发言3次

candidate_names = [
    "张伟",
    "王芳",
    "李娜",
    "刘强",
    "陈静",
    "杨帆",
    "赵敏",
    "黄伟",
    "周杰",
    "吴磊",
    "徐璐",
    "孙悦",
    "马丽",
    "朱琳",
    "胡军",
    "林峰",
    "郭涛",
    "何平",
    "高翔",
    "罗丹",
    "梁波",
    "宋佳",
    "唐艳",
    "韩冰",
    "冯刚",
    "董浩",
    "程雪",
    "曹阳",
    "邓婕",
    "彭帅",
    "蒋欣",
    "蔡明",
    "贾玲",
    "潘斌",
    "崔健",
    "谢楠",
    "沈凌",
    "韩红",
    "姚晨",
    "吴京",
]


def get_player_name() -> str:
    """生成玩家姓名。"""
    return candidate_names.pop(np.random.randint(len(candidate_names)))


def check_winning(
    alive_agents: list,
    wolf_agents: list,
) -> str | None:
    """检查是否游戏结束并返回胜利消息。"""
    if len(wolf_agents) * 2 >= len(alive_agents):
        return Prompts.to_all_wolf_win.format(
            n_werewolves=(
                f"{len(wolf_agents)}"
                + f"（{names_to_str([_.name for _ in wolf_agents])}）"
            ),
            n_villagers=len(alive_agents) - len(wolf_agents),
        )
    if alive_agents and not wolf_agents:
        return Prompts.to_all_village_win
    return None


def majority_vote(votes: list[str]) -> tuple:
    """返回票数最多的候选人及统计。"""
    result = max(set(votes), key=votes.count)
    names, counts = np.unique(votes, return_counts=True)
    conditions = "，".join(
        [f"{name}：{count}票" for name, count in zip(names, counts)],
    )
    return result, conditions


def names_to_str(agents: list[str] | list[ReActAgent]) -> str:
    """返回以中文符号连接的玩家姓名字符串。"""
    if not agents:
        return ""

    if len(agents) == 1:
        if isinstance(agents[0], ReActAgent):
            return agents[0].name
        return agents[0]

    names = []
    for agent in agents:
        if isinstance(agent, ReActAgent):
            names.append(agent.name)
        else:
            names.append(agent)

    if len(names) == 2:
        return names[0] + "和" + names[1]
    return "、".join([*names[:-1], "和" + names[-1]])


class EchoAgent(AgentBase):
    """复读代理：按主持人口吻转发消息。"""

    def __init__(self) -> None:
        super().__init__()
        self.name = "主持人"

    async def reply(self, content: str) -> Msg:
        """以主持人身份重复内容。"""
        msg = Msg(
            self.name,
            content,
            role="assistant",
        )
        await self.print(msg)
        return msg

    async def handle_interrupt(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Msg:
        """处理中断。"""

    async def observe(self, msg: Msg | list[Msg] | None) -> None:
        """观察用户消息。"""
