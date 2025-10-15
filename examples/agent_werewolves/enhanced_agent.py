# -*- coding: utf-8 -*-
"""增强版狼人杀 Agent 示例。

这个示例展示了如何创建一个自定义 Agent 来改进游戏策略。
主要改进点：
1. 增强的系统提示词
2. 更详细的角色指导
3. 符合比赛要求的接口实现
"""

import sys
from pathlib import Path

# 添加游戏目录到路径
game_dir = Path(__file__).parent.parent / "game" / "werewolves"
sys.path.insert(0, str(game_dir))

from prompt import Prompts
from utils import EchoAgent, get_player_name

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.model import OpenAIChatModel

from main import get_model

class EnhancedWerewolfAgent(ReActAgent):
    """增强版狼人杀 Agent。

    这是一个示例实现，展示如何在 ReActAgent 基础上进行改进。
    符合比赛的所有要求：
    - 实现 observe 方法
    - 支持 __call__(msg) 和 __call__() 调用
    - 支持结构化输出
    - 实现 state_dict() 和 load_state_dict()
    """

    def __init__(self, name: str, role: str, **kwargs) -> None:
        """初始化增强版 Agent。

        Args:
            name: Agent 名称
            role: 角色类型
            **kwargs: 其他参数
        """
        # 使用增强的系统提示词
        enhanced_sys_prompt = self._get_enhanced_sys_prompt(name, role)

        # 调用父类初始化
        super().__init__(
            name=name,
            sys_prompt=enhanced_sys_prompt,
            model=kwargs.get("model") or self._get_default_model(),
            formatter=kwargs.get("formatter") or DashScopeMultiAgentFormatter(),
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["model", "formatter", "sys_prompt"]
            },
        )

        self.role = role

    def _get_default_model(self):
        """获取默认模型。"""
        return get_model("dashscope")

    def _get_enhanced_sys_prompt(self, name: str, role: str) -> str:
        """获取增强的系统提示词。

        这里可以根据不同角色定制更详细的策略指导。
        """
        base_prompt = Prompts.system_prompt.format(
            player_name=name,
            guidance=getattr(Prompts, f"notes_{role}"),
        )

        # 添加额外的策略指导
        enhanced_guidance = """

## 增强策略指导

### 逻辑推理
- 仔细分析每个玩家的发言，寻找矛盾和不一致之处
- 跟踪夜间死亡模式，推断特殊角色的使用情况
- 注意投票行为，狼人可能会集体投票

### 信息管理
- 记住关键信息：谁查验了谁、谁声称什么角色
- 不要过早暴露自己的身份（如果是特殊角色）
- 适时分享信息以建立信任

### 团队协作
- 保护已知的队友
- 识别并支持可信的特殊角色
- 协调投票以淘汰嫌疑玩家
"""
        return base_prompt + enhanced_guidance


# Agent 工厂函数（评估系统需要）
async def agent_factory(role: str) -> ReActAgent:
    """创建 Agent 的工厂函数（替换式对比模式）。

    这个函数是评估系统调用的入口。
    采用"替换式"对比：只对特定角色使用增强版 Agent，其他角色使用基线 Agent。
    这样可以对比"增强版狼人 Agent" vs "基线狼人 Agent"的胜率差异。

    你可以修改 ENHANCED_ROLES 来选择要增强的角色。

    Args:
        role: 角色类型 (villager, werewolf, seer, witch, hunter)

    Returns:
        ReActAgent 或 EnhancedWerewolfAgent 实例
    """
    # 配置：选择要使用增强版 Agent 的角色
    # 示例：只增强狼人，其他角色使用基线
    ENHANCED_ROLES = ["werewolf"]  # 可以修改为 ["seer", "witch"] 等

    name = get_player_name()
    moderator = EchoAgent()
    role_names = {
        "villager": "村民",
        "werewolf": "狼人",
        "seer": "预言家",
        "witch": "女巫",
        "hunter": "猎人",
    }

    # 判断是否使用增强版 Agent
    if role in ENHANCED_ROLES:
        # 使用增强版 Agent
        agent = EnhancedWerewolfAgent(name=name, role=role)
    else:
        # 使用基线 ReActAgent
        from main import default_agent_factory

        agent = await default_agent_factory(role, {name: role}, moderator)
        return agent  # 基线 Agent 已经通知身份了

    # 通知增强版 Agent 的身份
    await agent.observe(
        await moderator(
            f"[仅限{name}] {name}，你的身份是 {role_names[role]}。",
        ),
    )

    return agent
