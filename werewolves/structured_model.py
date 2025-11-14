# -*- coding: utf-8 -*-
"""狼人杀游戏中使用的结构化输出模型。"""

from typing import Literal

from pydantic import BaseModel, Field

from agentscope.agent import AgentBase


class DiscussionModel(BaseModel):
    """讨论的输出格式。"""

    reach_agreement: bool = Field(
        description="是否达成一致意见",
    )


def get_vote_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家名称获取投票模型。"""

    class VoteModel(BaseModel):
        """投票的输出格式。"""

        vote: Literal[tuple(_.name for _ in agents)] = Field(  # type: ignore
            description="你想投票的玩家名称",
        )

    return VoteModel


class WitchResurrectModel(BaseModel):
    """女巫复活动作的输出格式。"""

    resurrect: bool = Field(
        description="是否要复活玩家",
    )


def get_poison_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家名称获取毒药模型。"""

    class WitchPoisonModel(BaseModel):
        """女巫下毒动作的输出格式。"""

        poison: bool = Field(
            description="是否要使用毒药",
        )
        name: (
            Literal[  # type: ignore
                tuple(_.name for _ in agents)
            ]
            | None
        ) = Field(
            description="你想毒杀的玩家名称，如果不想毒杀任何人，留空即可",
            default=None,
        )

    return WitchPoisonModel


def get_seer_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家名称获取预言家模型。"""

    class SeerModel(BaseModel):
        """预言家动作的输出格式。"""

        name: Literal[tuple(_.name for _ in agents)] = Field(  # type: ignore
            description="你想查验的玩家名称",
        )

    return SeerModel


def get_hunter_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家智能体获取猎人模型。"""

    class HunterModel(BaseModel):
        """猎人动作的输出格式。"""

        shoot: bool = Field(
            description="是否要使用开枪能力",
        )
        name: (
            Literal[  # type: ignore
                tuple(_.name for _ in agents)
            ]
            | None
        ) = Field(
            description="你想射击的玩家名称，如果不想使用能力，留空即可",
            default=None,
        )

    return HunterModel
