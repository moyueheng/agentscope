# -*- coding: utf-8 -*-
"""狼人杀游戏的结构化输出模型。"""

from typing import Literal

from pydantic import BaseModel, Field

from agentscope.agent import AgentBase


class DiscussionModel(BaseModel):
    """讨论阶段的输出格式。"""

    reach_agreement: bool = Field(
        description="是否已达成一致",
    )


def get_vote_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家姓名生成投票模型。"""

    class VoteModel(BaseModel):
        """投票的输出格式"""

        vote: Literal[tuple(_.name for _ in agents)] = Field(  # type: ignore
            description="你要投票给的玩家姓名, 不允许弃票, 必须投票给一个玩家",
        )

    return VoteModel


class WitchResurrectModel(BaseModel):
    """女巫复活行为的输出格式。"""

    resurrect: bool = Field(
        description="是否要复活该玩家",
    )


def get_poison_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家姓名生成女巫毒药模型。"""

    class WitchPoisonModel(BaseModel):
        """女巫使用毒药的输出格式。"""

        poison: bool = Field(
            description="是否要使用毒药",
        )
        name: (
            Literal[  # type: ignore
                tuple(_.name for _ in agents)
            ]
            | None
        ) = Field(
            description="你要毒杀的玩家姓名；如果不毒杀任何人，留空即可",
            default=None,
        )

    return WitchPoisonModel


def get_seer_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家姓名生成预言家模型。"""

    class SeerModel(BaseModel):
        """预言家查验的输出格式。"""

        name: Literal[tuple(_.name for _ in agents)] = Field(  # type: ignore
            description="你要查验的玩家姓名",
        )

    return SeerModel


def get_hunter_model(agents: list[AgentBase]) -> type[BaseModel]:
    """根据玩家代理对象生成猎人模型。"""

    class HunterModel(BaseModel):
        """猎人开枪的输出格式。"""

        shoot: bool = Field(
            description="是否要使用开枪技能",
        )
        name: (
            Literal[  # type: ignore
                tuple(_.name for _ in agents)
            ]
            | None
        ) = Field(
            description="你要开枪击杀的玩家姓名；如果不使用该技能，留空即可",
            default=None,
        )

    return HunterModel
