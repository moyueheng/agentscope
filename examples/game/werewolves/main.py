# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches, too-many-statements, no-name-in-module
"""使用 agentscope 实现的狼人杀游戏。"""

import asyncio
import os
from datetime import datetime
from typing import Awaitable, Callable

from game_result import GameResult, PlayerInfo
from prompt import Prompts
from structured_output import (
    DiscussionModel,
    WitchResurrectModel,
    get_hunter_model,
    get_poison_model,
    get_seer_model,
    get_vote_model,
)
from utils import (
    MAX_DISCUSSION_ROUND,
    MAX_GAME_ROUND,
    EchoAgent,
    check_winning,
    get_player_name,
    majority_vote,
    names_to_str,
)

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.pipeline import MsgHub, fanout_pipeline, sequential_pipeline

# 类型定义
AgentFactory = Callable[[str], Awaitable[ReActAgent]]


def get_model(provider: str = "dashscope") -> DashScopeChatModel | OpenAIChatModel:
    """根据模型供应商返回对应的模型实例。"""
    return DashScopeChatModel(
        model_name="qwen-max",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        enable_thinking=True,
    )


async def default_agent_factory(
    role: str, name_to_role: dict[str, str], moderator: EchoAgent
) -> ReActAgent:
    """默认的 Agent 工厂函数。"""
    name = get_player_name()
    name_to_role[name] = role
    agent = ReActAgent(
        name=name,
        sys_prompt=Prompts.system_prompt.format(
            player_name=name,
            guidance=getattr(Prompts, f"notes_{role}"),
        ),
        model=get_model("dashscope"),
        formatter=DashScopeMultiAgentFormatter(),
    )
    await agent.observe(
        await moderator(
            f"[仅限{name}] {name}，你的身份是 { {'villager': '村民', 'werewolf': '狼人', 'seer': '预言家', 'witch': '女巫', 'hunter': '猎人'}[role] }。",
        ),
    )
    return agent


class WerewolfGame:
    """狼人杀游戏类。"""

    def __init__(
        self,
        game_id: int = 0,
        agent_factory: AgentFactory | None = None,
    ) -> None:
        """初始化游戏。

        Args:
            game_id: 游戏 ID
            agent_factory: 可选的 Agent 工厂函数
        """
        self.game_id = game_id
        self.agent_factory = agent_factory
        self.name_to_role: dict[str, str] = {}
        self.moderator = EchoAgent()
        self.healing = True
        self.poison = True
        self.villagers: list[ReActAgent] = []
        self.werewolves: list[ReActAgent] = []
        self.seer: list[ReActAgent] = []
        self.witch: list[ReActAgent] = []
        self.hunter: list[ReActAgent] = []
        self.current_alive: list[ReActAgent] = []
        self.current_round = 0
        self.start_time = datetime.now()

    async def create_player(self, role: str) -> ReActAgent:
        """创建包含姓名与角色的玩家代理。"""
        if self.agent_factory:
            agent = await self.agent_factory(role)
            self.name_to_role[agent.name] = role
            return agent
        else:
            return await default_agent_factory(role, self.name_to_role, self.moderator)

    async def hunter_stage(self, hunter_agent: ReActAgent) -> str | None:
        """猎人阶段可能发生在两处：夜晚被击杀或白天被投票淘汰。为避免重复逻辑，这里单独定义该流程。"""
        msg_hunter = await hunter_agent(
            await self.moderator(Prompts.to_hunter.format(name=hunter_agent.name)),
            structured_model=get_hunter_model(self.current_alive),
        )
        if msg_hunter.metadata.get("shoot"):
            return msg_hunter.metadata.get("name", None)
        return None

    def update_players(self, dead_players: list[str]) -> None:
        """根据死亡名单更新全局的存活玩家列表。"""
        self.werewolves = [_ for _ in self.werewolves if _.name not in dead_players]
        self.villagers = [_ for _ in self.villagers if _.name not in dead_players]
        self.seer = [_ for _ in self.seer if _.name not in dead_players]
        self.hunter = [_ for _ in self.hunter if _.name not in dead_players]
        self.witch = [_ for _ in self.witch if _.name not in dead_players]
        self.current_alive = [
            _ for _ in self.current_alive if _.name not in dead_players
        ]

    def get_game_result(self, winner: str) -> GameResult:
        """生成游戏结果。"""
        all_players = sorted(
            self.werewolves + self.villagers + self.seer + self.witch + self.hunter,
            key=lambda _: _.name,
        )
        players_info = [
            PlayerInfo(
                name=player.name,
                role=self.name_to_role[player.name],
                survived=player in self.current_alive,
                rounds_survived=self.current_round
                if player in self.current_alive
                else 0,
            )
            for player in all_players
        ]
        return GameResult(
            game_id=self.game_id,
            winner=winner,
            total_rounds=self.current_round,
            players=players_info,
            timestamp=self.start_time.isoformat(),
        )

    async def run(self) -> GameResult:
        """运行一局游戏，返回游戏结果。"""
        # 创建玩家, 初始化系统提示词和身份信息
        self.villagers = [await self.create_player("villager") for _ in range(3)]
        self.werewolves = [await self.create_player("werewolf") for _ in range(3)]
        self.seer = [await self.create_player("seer")]
        self.witch = [await self.create_player("witch")]
        self.hunter = [await self.create_player("hunter")]
        # 按姓名顺序发言
        self.current_alive = sorted(
            self.werewolves + self.villagers + self.seer + self.witch + self.hunter,
            key=lambda _: _.name,
        )

        # 游戏开始！
        for round_num in range(MAX_GAME_ROUND):
            self.current_round = round_num + 1
            # 创建用于全体广播的 MsgHub
            async with MsgHub(
                participants=self.current_alive,
                enable_auto_broadcast=False,  # 手动广播模式
                name="all_players",
            ) as all_players_hub:
                # 夜晚阶段
                await all_players_hub.broadcast(
                    await self.moderator(Prompts.to_all_night),
                )
                killed_player, poisoned_player, shot_player = (
                    None,
                    None,
                    None,
                )  # 被杀死, 被毒死, 被猎人一换一

                # 狼人讨论
                async with MsgHub(
                    self.werewolves,
                    enable_auto_broadcast=True,
                    announcement=await self.moderator(
                        Prompts.to_wolves_discussion.format(
                            werewolve_names=names_to_str(self.werewolves),
                            villager_names=names_to_str(self.villagers),
                        ),
                    ),
                ) as werewolves_hub:
                    # 狼人讨论阶段：轮流发言，直到达成一致或达到最大轮次
                    agreement_reached = False
                    # 总发言次数 = 最大讨论轮次 × 狼人数量
                    total_turns = MAX_DISCUSSION_ROUND * len(self.werewolves)
                    for turn in range(1, total_turns + 1):
                        # 按顺序选出当前发言的狼人
                        current_wolf_idx = (turn - 1) % len(self.werewolves)
                        current_wolf = self.werewolves[current_wolf_idx]
                        # 让当前狼人发言并返回结构化结果
                        res = await current_wolf(structured_model=DiscussionModel)
                        # 每完整轮次后检查是否全员达成一致
                        if turn % len(self.werewolves) == 0:
                            if res.metadata.get("reach_agreement"):
                                agreement_reached = True
                                break
                    # 如果循环结束仍未达成一致，res 保留最后一次发言结果

                    # 狼人投票
                    # 关闭自动广播以避免跟票
                    werewolves_hub.set_auto_broadcast(False)
                    msgs_vote = await fanout_pipeline(
                        self.werewolves,
                        msg=await self.moderator(content=Prompts.to_wolves_vote),
                        structured_model=get_vote_model(self.current_alive),
                        enable_gather=False,
                    )
                    killed_player, votes = majority_vote(
                        [_.metadata.get("vote") for _ in msgs_vote],
                    )
                    # 延后广播投票结果
                    await werewolves_hub.broadcast(
                        [
                            *msgs_vote,
                            await self.moderator(
                                Prompts.to_wolves_res.format(votes, killed_player),
                            ),
                        ],
                    )

                # 女巫回合
                await all_players_hub.broadcast(
                    await self.moderator(Prompts.to_all_witch_turn),
                )
                msg_witch_poison = None
                for agent in self.witch:
                    # 女巫不能救自己
                    msg_witch_resurrect = None
                    if self.healing and killed_player != agent.name:
                        msg_witch_resurrect = await agent(
                            await self.moderator(
                                Prompts.to_witch_resurrect.format(
                                    witch_name=agent.name,
                                    dead_name=killed_player,
                                ),
                            ),
                            structured_model=WitchResurrectModel,
                        )
                        if msg_witch_resurrect.metadata.get("resurrect"):
                            killed_player = None
                            self.healing = False

                    if self.poison and not (
                        msg_witch_resurrect
                        and msg_witch_resurrect.metadata["resurrect"]
                    ):
                        msg_witch_poison = await agent(
                            await self.moderator(
                                Prompts.to_witch_poison.format(
                                    witch_name=agent.name,
                                ),
                            ),
                            structured_model=get_poison_model(self.current_alive),
                        )
                        if msg_witch_poison.metadata.get("poison"):
                            poisoned_player = msg_witch_poison.metadata.get("name")
                            self.poison = False

                # 预言家回合
                await all_players_hub.broadcast(
                    await self.moderator(Prompts.to_all_seer_turn),
                )
                for agent in self.seer:
                    msg_seer = await agent(
                        await self.moderator(
                            Prompts.to_seer.format(
                                agent.name,
                                names_to_str(self.current_alive),
                            ),
                        ),
                        structured_model=get_seer_model(self.current_alive),
                    )
                    if msg_seer.metadata.get("name"):
                        player = msg_seer.metadata["name"]
                        await agent.observe(
                            await self.moderator(
                                Prompts.to_seer_result.format(
                                    agent_name=player,
                                    role=self.name_to_role[player],
                                ),
                            ),
                        )

                # 猎人回合
                for agent in self.hunter:
                    # 若被夜晚击杀，且不是女巫的毒药
                    if killed_player == agent.name and poisoned_player != agent.name:
                        shot_player = await self.hunter_stage(agent)

                # 更新存活玩家列表
                dead_tonight = [killed_player, poisoned_player, shot_player]
                self.update_players(dead_tonight)

                # 白天阶段
                if len([_ for _ in dead_tonight if _]) > 0:
                    await all_players_hub.broadcast(
                        await self.moderator(
                            Prompts.to_all_day.format(
                                names_to_str([_ for _ in dead_tonight if _]),
                            ),
                        ),
                    )
                else:
                    await all_players_hub.broadcast(
                        await self.moderator(Prompts.to_all_peace),
                    )

                # 检查胜负
                res = check_winning(self.current_alive, self.werewolves)
                if res:
                    await self.moderator(res)
                    winner = "werewolves" if "狼人阵营获胜" in res else "villagers"
                    return self.get_game_result(winner)

                # 讨论阶段
                await all_players_hub.broadcast(
                    await self.moderator(
                        Prompts.to_all_discuss.format(
                            names=names_to_str(self.current_alive),
                        ),
                    ),
                )
                # 开启自动广播以进行讨论
                all_players_hub.set_auto_broadcast(True)
                await sequential_pipeline(self.current_alive)
                # 关闭自动广播以避免泄露信息
                all_players_hub.set_auto_broadcast(False)

                # 投票阶段
                msgs_vote = await fanout_pipeline(
                    self.current_alive,
                    await self.moderator(
                        Prompts.to_all_vote.format(names_to_str(self.current_alive)),
                    ),
                    structured_model=get_vote_model(self.current_alive),
                    enable_gather=False,
                )
                voted_player, votes = majority_vote(
                    [_.metadata.get("vote") for _ in msgs_vote],
                )
                await all_players_hub.broadcast(
                    [
                        *msgs_vote,
                        await self.moderator(
                            Prompts.to_all_res.format(votes, voted_player),
                        ),
                    ],
                )

                shot_player = None
                for agent in self.hunter:
                    if voted_player == agent.name:
                        shot_player = await self.hunter_stage(agent)
                        if shot_player:
                            await all_players_hub.broadcast(
                                await self.moderator(
                                    Prompts.to_all_hunter_shoot.format(
                                        shot_player,
                                    ),
                                ),
                            )

                # 更新存活玩家列表
                dead_today = [voted_player, shot_player]
                self.update_players(dead_today)

                # 检查胜负
                res = check_winning(self.current_alive, self.werewolves)
                if res:
                    await self.moderator(res)
                    winner = "werewolves" if "狼人阵营获胜" in res else "villagers"
                    return self.get_game_result(winner)

        # 如果达到最大回合数，返回当前结果
        winner = "werewolves" if len(self.werewolves) > 0 else "villagers"
        return self.get_game_result(winner)


async def main() -> None:
    """狼人杀游戏入口函数（保持向后兼容）。"""
    # 如需启用 Studio，请取消以下注释
    # import agentscope
    # agentscope.init(
    #     studio_url="http://localhost:3000",
    #     project="Werewolf Game",
    # )
    game = WerewolfGame()
    result = await game.run()
    print(f"\n游戏结束！胜利方：{result.winner}")
    print(f"总轮数：{result.total_rounds}")


if __name__ == "__main__":
    asyncio.run(main())
