# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches, too-many-statements, no-name-in-module
"""使用 agentscope 实现的狼人杀游戏。"""

import asyncio
import os

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

NAME_TO_ROLE = {}
moderator = EchoAgent()
healing, poison = True, True
villagers, werewolves, seer, witch, hunter = [], [], [], [], []
current_alive = []


async def hunter_stage(
    hunter_agent: ReActAgent,
) -> str | None:
    """猎人阶段可能发生在两处：夜晚被击杀或白天被投票淘汰。为避免重复逻辑，这里单独定义该流程。"""
    global current_alive, moderator
    msg_hunter = await hunter_agent(
        await moderator(Prompts.to_hunter.format(name=hunter_agent.name)),
        structured_model=get_hunter_model(current_alive),
    )
    if msg_hunter.metadata.get("shoot"):
        return msg_hunter.metadata.get("name", None)
    return None


def update_players(dead_players: list[str]) -> None:
    """根据死亡名单更新全局的存活玩家列表。"""
    global werewolves, villagers, seer, hunter, witch, current_alive
    werewolves = [_ for _ in werewolves if _.name not in dead_players]
    villagers = [_ for _ in villagers if _.name not in dead_players]
    seer = [_ for _ in seer if _.name not in dead_players]
    hunter = [_ for _ in hunter if _.name not in dead_players]
    witch = [_ for _ in witch if _.name not in dead_players]
    current_alive = [_ for _ in current_alive if _.name not in dead_players]


def get_model(provider: str) -> DashScopeChatModel:
    """根据模型供应商返回对应的模型实例。"""
    if provider == "dashscope":
        return DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
            enable_thinking=True,
        )
    if provider == "quwan":
        return OpenAIChatModel(
            model_name="Qwen/Qwen3-32B",
            api_key="sk-quwan-jarvis",
            # enable_thinking=True,
            client_args={
                "base_url": "http://ray.ttyuyin.com:10001/vllm-qwen3-32b/v1",
            },
        )
    raise ValueError(f"Unsupported model provider: {provider}")


async def create_player(role: str) -> ReActAgent:
    """创建包含姓名与角色的玩家代理。"""
    name = get_player_name()
    global NAME_TO_ROLE
    NAME_TO_ROLE[name] = role
    agent = ReActAgent(
        name=name,
        sys_prompt=Prompts.system_prompt.format(
            player_name=name,
            guidance=getattr(Prompts, f"notes_{role}"),
        ),
        model=get_model("quwan"),
        formatter=DashScopeMultiAgentFormatter(),
    )
    await agent.observe(
        await moderator(
            f"[仅限{name}] {name}，你的身份是 { {'villager': '村民', 'werewolf': '狼人', 'seer': '预言家', 'witch': '女巫', 'hunter': '猎人'}[role] }。",
        ),
    )
    return agent


async def main() -> None:
    """狼人杀游戏入口函数。"""
    # 如需启用 Studio，请取消以下注释
    # import agentscope
    # agentscope.init(
    #     studio_url="http://localhost:3000",
    #     project="Werewolf Game",
    # )
    global healing, poison, villagers, werewolves, seer, witch, hunter
    global current_alive
    # 创建玩家, 初始化系统提示词和身份信息
    villagers = [await create_player("villager") for _ in range(3)]
    werewolves = [await create_player("werewolf") for _ in range(3)]
    seer = [await create_player("seer")]
    witch = [await create_player("witch")]
    hunter = [await create_player("hunter")]
    # 按姓名顺序发言
    current_alive = sorted(
        werewolves + villagers + seer + witch + hunter,
        key=lambda _: _.name,
    )

    # 游戏开始！
    for _ in range(MAX_GAME_ROUND):
        # 创建用于全体广播的 MsgHub
        async with MsgHub(
            participants=current_alive,
            enable_auto_broadcast=False,  # 手动广播模式
            name="all_players",
        ) as all_players_hub:
            # 夜晚阶段
            await all_players_hub.broadcast(
                await moderator(Prompts.to_all_night),
            )
            killed_player, poisoned_player, shot_player = None, None, None # 被杀死, 被毒死, 被猎人一换一

            # 狼人讨论
            async with MsgHub(
                werewolves,
                enable_auto_broadcast=True,
                announcement=await moderator(
                    Prompts.to_wolves_discussion.format(
                        werewolve_names=names_to_str(werewolves),
                        villager_names=names_to_str(villagers),
                    ),
                ),
            ) as werewolves_hub:
                # 狼人讨论阶段：轮流发言，直到达成一致或达到最大轮次
                agreement_reached = False
                # 总发言次数 = 最大讨论轮次 × 狼人数量
                total_turns = MAX_DISCUSSION_ROUND * len(werewolves)
                for turn in range(1, total_turns + 1):
                    # 按顺序选出当前发言的狼人
                    current_wolf_idx = (turn - 1) % len(werewolves)
                    current_wolf = werewolves[current_wolf_idx]
                    # 让当前狼人发言并返回结构化结果
                    res = await current_wolf(structured_model=DiscussionModel) # TODO 本质是什么, LLM是如何处理结构化输出
                    # 每完整轮次后检查是否全员达成一致
                    if turn % len(werewolves) == 0:
                        if res.metadata.get("reach_agreement"):
                            agreement_reached = True
                            break
                # 如果循环结束仍未达成一致，res 保留最后一次发言结果

                # 狼人投票
                # 关闭自动广播以避免跟票
                werewolves_hub.set_auto_broadcast(False)
                msgs_vote = await fanout_pipeline(
                    werewolves,
                    msg=await moderator(content=Prompts.to_wolves_vote),
                    structured_model=get_vote_model(current_alive),
                    enable_gather=False,
                )
                killed_player, votes = majority_vote(
                    [_.metadata.get("vote") for _ in msgs_vote],
                )
                # 延后广播投票结果
                await werewolves_hub.broadcast(
                    [
                        *msgs_vote,
                        await moderator(
                            Prompts.to_wolves_res.format(votes, killed_player),
                        ),
                    ],
                )

            # 女巫回合
            await all_players_hub.broadcast(
                await moderator(Prompts.to_all_witch_turn),
            )
            msg_witch_poison = None
            for agent in witch:
                # 女巫不能救自己
                msg_witch_resurrect = None
                if healing and killed_player != agent.name:
                    msg_witch_resurrect = await agent(
                        await moderator(
                            Prompts.to_witch_resurrect.format(
                                witch_name=agent.name,
                                dead_name=killed_player,
                            ),
                        ),
                        structured_model=WitchResurrectModel,
                    )
                    if msg_witch_resurrect.metadata.get("resurrect"):
                        killed_player = None
                        healing = False

                if poison and not (
                    msg_witch_resurrect and msg_witch_resurrect.metadata["resurrect"]
                ):
                    msg_witch_poison = await agent(
                        await moderator(
                            Prompts.to_witch_poison.format(
                                witch_name=agent.name,
                            ),
                        ),
                        structured_model=get_poison_model(current_alive),
                    )
                    if msg_witch_poison.metadata.get("poison"):
                        poisoned_player = msg_witch_poison.metadata.get("name")
                        poison = False

            # 预言家回合
            await all_players_hub.broadcast(
                await moderator(Prompts.to_all_seer_turn),
            )
            for agent in seer:
                msg_seer = await agent(
                    await moderator(
                        Prompts.to_seer.format(
                            agent.name,
                            names_to_str(current_alive),
                        ),
                    ),
                    structured_model=get_seer_model(current_alive),
                )
                if msg_seer.metadata.get("name"):
                    player = msg_seer.metadata["name"]
                    await agent.observe(
                        await moderator(
                            Prompts.to_seer_result.format(
                                agent_name=player,
                                role=NAME_TO_ROLE[player],
                            ),
                        ),
                    )

            # 猎人回合
            for agent in hunter:
                # 若被夜晚击杀，且不是女巫的毒药
                if killed_player == agent.name and poisoned_player != agent.name:
                    shot_player = await hunter_stage(agent)

            # 更新存活玩家列表
            dead_tonight = [killed_player, poisoned_player, shot_player]
            update_players(dead_tonight)

            # 白天阶段
            if len([_ for _ in dead_tonight if _]) > 0:
                await all_players_hub.broadcast(
                    await moderator(
                        Prompts.to_all_day.format(
                            names_to_str([_ for _ in dead_tonight if _]),
                        ),
                    ),
                )
            else:
                await all_players_hub.broadcast(
                    await moderator(Prompts.to_all_peace),
                )

            # 检查胜负
            res = check_winning(current_alive, werewolves)
            if res:
                await moderator(res)
                return

            # 讨论阶段
            await all_players_hub.broadcast(
                await moderator(
                    Prompts.to_all_discuss.format(
                        names=names_to_str(current_alive),
                    ),
                ),
            )
            # 开启自动广播以进行讨论
            all_players_hub.set_auto_broadcast(True)
            await sequential_pipeline(current_alive) # 所有人顺序发言, 因为开启了自动广播, 所有消息都会进入all_players_hub
            # 关闭自动广播以避免泄露信息
            all_players_hub.set_auto_broadcast(False)

            # 投票阶段
            msgs_vote = await fanout_pipeline(
                current_alive,
                await moderator(
                    Prompts.to_all_vote.format(names_to_str(current_alive)),
                ),
                structured_model=get_vote_model(current_alive),
                enable_gather=False,
            )
            voted_player, votes = majority_vote(
                [_.metadata.get("vote") for _ in msgs_vote],
            )
            await all_players_hub.broadcast(
                [
                    *msgs_vote,
                    await moderator(
                        Prompts.to_all_res.format(votes, voted_player),
                    ),
                ],
            )

            shot_player = None
            for agent in hunter:
                if voted_player == agent.name:
                    shot_player = await hunter_stage(agent)
                    if shot_player:
                        await all_players_hub.broadcast(
                            await moderator(
                                Prompts.to_all_hunter_shoot.format(
                                    shot_player,
                                ),
                            ),
                        )

            # 更新存活玩家列表
            dead_today = [voted_player, shot_player]
            update_players(dead_today)

            # 检查胜负
            res = check_winning(current_alive, werewolves)
            if res:
                await moderator(res)
                return


if __name__ == "__main__":
    asyncio.run(main())
