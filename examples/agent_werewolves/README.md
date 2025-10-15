# 自定义狼人杀 Agent 开发指南

本目录提供了自定义狼人杀 Agent 的示例实现和开发指南。

## 快速开始

### 1. 查看示例 Agent

`enhanced_agent.py` 提供了一个完整的示例实现，展示了如何在 `ReActAgent` 基础上创建自定义 Agent。

### 2. 运行评估

```bash
# 切换到游戏目录
cd examples/game/werewolves

# 运行基线测试
python evaluate.py --num-games 10 --mode baseline

# 运行自定义 Agent 测试
python evaluate.py --num-games 10 --mode custom \
  --custom-agent ../../agent_werewolves/enhanced_agent.py
```

### 3. 对比结果

系统会自动生成评估报告，显示胜率统计和对比结果。

## Agent 开发要求

根据比赛规则，你的自定义 Agent 必须满足以下要求：

### 1. 必须实现的接口

```python
class CustomAgent(ReActAgent):
    async def observe(self, msg: Msg | list[Msg] | None) -> None:
        """观察和接收消息"""
        pass

    async def __call__(self, msg: Msg | None = None, **kwargs):
        """处理消息并返回响应"""
        pass

    async def reply(self, msg: Msg) -> Msg:
        """生成回复"""
        pass

    def state_dict(self) -> dict:
        """导出状态"""
        pass

    def load_state_dict(self, state: dict) -> None:
        """加载状态"""
        pass
```

### 2. 支持结构化输出

Agent 必须支持以下调用方式：

```python
# 基本调用
await agent(msg)

# 无参数调用
await agent()

# 结构化输出
await agent(msg, structured_model=StructuredModel)
```

### 3. Agent 工厂函数（替换式对比模式）

你的模块必须提供 `agent_factory` 函数。**重要**：采用"替换式"对比模式，只对特定角色使用增强版 Agent：

```python
async def agent_factory(role: str) -> ReActAgent:
    """创建 Agent 的工厂函数。

    采用"替换式"对比：只对特定角色使用增强版 Agent，其他角色使用基线。
    这样可以对比"增强版狼人" vs "基线狼人"的胜率差异。

    Args:
        role: 角色类型 (villager, werewolf, seer, witch, hunter)

    Returns:
        符合要求的 Agent 实例
    """
    # 配置：选择要增强的角色
    ENHANCED_ROLES = ["werewolf"]  # 例如：只增强狼人

    if role in ENHANCED_ROLES:
        # 使用你的增强版 Agent
        agent = MyEnhancedAgent(name=name, role=role)
    else:
        # 使用基线 Agent
        from main import default_agent_factory
        agent = await default_agent_factory(role, {name: role}, moderator)
        return agent

    # 通知身份
    # ...
    return agent
```

**为什么这样设计？**

- **对比效果清晰**：例如只增强狼人，可以看到"增强狼人 vs 基线狼人"的胜率差异
- **公平对比**：一局游戏中，3 个狼人都是增强版，其他角色都是基线
- **避免混合**：不会出现同一角色既有基线又有增强的情况

## 改进策略建议

### 1. 系统提示词优化

- 为不同角色定制详细的策略指导
- 强调逻辑推理和信息分析
- 提供具体的决策框架

### 2. 记忆管理

- 跟踪游戏历史信息
- 记录关键事件和推理
- 维护玩家行为模式

### 3. 策略优化

根据角色优化策略：

#### 狼人策略
- 隐藏身份，伪装成村民或特殊角色
- 分散投票以避免暴露
- 优先击杀预言家和女巫

#### 预言家策略
- 谨慎选择查验目标
- 适时公布身份以获得信任
- 分享查验结果指导投票

#### 女巫策略
- 合理使用解药和毒药
- 保护关键角色
- 根据局势决定是否用药

#### 猎人策略
- 隐藏身份直到关键时刻
- 选择最佳时机带走嫌疑狼人
- 配合队友淘汰狼人

#### 村民策略
- 积极推理，寻找狼人
- 保护预言家等特殊角色
- 协调投票

## 评估指标

评估系统会统计以下指标：

1. **胜率统计**
   - 村民阵营胜率
   - 狼人阵营胜率

2. **角色统计**
   - 各角色的胜率
   - 各角色的存活率

3. **游戏时长**
   - 平均游戏轮数

4. **对比结果**
   - 与基线 Agent 的胜率差异
   - 统计显著性（样本量越大越可靠）

## 调试技巧

### 1. 单局测试

```bash
# 直接运行游戏查看详细日志
cd examples/game/werewolves
python main.py
```

### 2. 小规模评估

```bash
# 先运行少量局数快速验证
python evaluate.py --num-games 3 --mode custom --custom-agent <your_agent>.py
```

### 3. 大规模评估

```bash
# 确认策略有效后运行更多局数
python evaluate.py --num-games 50 --mode custom --custom-agent <your_agent>.py
```

## 常见问题

### Q: 如何访问游戏历史信息？

A: 可以通过 Agent 的 `memory` 属性访问对话历史。

### Q: 如何实现更复杂的推理逻辑？

A: 可以重写 `reply` 方法，在调用模型前后添加自定义逻辑。

### Q: 如何处理不同角色的不同策略？

A: 在 `__init__` 中根据 `role` 参数定制系统提示词和行为。

### Q: 评估系统如何调用我的 Agent？

A: 评估系统会导入你的模块并调用 `agent_factory(role)` 函数创建 Agent。

## 对比测试流程

### 测试增强狼人策略

```bash
cd examples/game/werewolves

# 1. 运行基线测试（所有角色都是基线 Agent）
python evaluate.py --num-games 20 --mode baseline --output baseline.json
# 输出：狼人阵营胜率: 45.0%

# 2. 运行增强狼人测试（狼人=增强版，其他=基线）
python evaluate.py --num-games 1 --mode custom \
  --custom-agent ../../agent_werewolves/enhanced_agent.py \
  --output enhanced.json
# 输出：狼人阵营胜率: 60.0% ⬆️ +15%
```

### 测试不同角色的增强效果

修改 `enhanced_agent.py` 中的配置：
```python
# 只增强预言家
ENHANCED_ROLES = ["seer"]

# 或增强多个角色
ENHANCED_ROLES = ["seer", "witch"]
```

**重要提示**：
- 每次修改 `ENHANCED_ROLES` 后，都要重新运行评估
- 对比基线和增强版的胜率差异
- 样本量越大（50+ 局）结果越可靠

## 示例代码说明

`enhanced_agent.py` 包含：

1. **EnhancedWerewolfAgent 类**: 继承自 `ReActAgent`，增强了系统提示词
2. **agent_factory 函数**: 创建 Agent 的工厂函数（**采用替换式对比模式**）
3. **ENHANCED_ROLES 配置**: 选择要增强的角色
4. **符合比赛要求**: 所有必需的接口都已实现（继承自父类）

你可以基于这个示例进行修改和扩展。

## 参考资源

- AgentScope 文档: https://doc.agentscope.io/
- 游戏主逻辑: `examples/game/werewolves/main.py`
- 提示词定义: `examples/game/werewolves/prompt.py`
- 工具函数: `examples/game/werewolves/utils.py`

