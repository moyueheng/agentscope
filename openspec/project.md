# Project Context

## Purpose
基于 AgentScope 1.0 框架构建智能狼人杀游戏 Agent，通过自主学习不断提升游戏水平。该 Agent 需要适应狼人杀游戏的不同角色，参与九人制狼人杀比赛，自主制定游戏策略并以获胜为最终目标。本项目是一个比赛项目，考察 Agent 在动态环境中的学习能力、适应能力和策略优化能力。

## Tech Stack
- **语言与版本**: Python 3.12
- **框架**: AgentScope 1.0 (多智能体框架)
- **大模型**: 百炼平台 qwen-max 模型 (DashScope)
- **环境管理**: uv
- **代码格式化**: ruff format
- **类型检查**: pyright
- **版本控制**: git

## Project Conventions

### Code Style
- **命名与结构**: 命名清晰、函数短小、模块职责单一
- **设计原则**: 避免"上帝对象"和深层继承，首选组合模式
- **格式化**: 统一使用 `ruff format` 进行代码格式化
- **类型标注**: 
  - 全量类型标注：接口、数据模型、返回值都必须标注
  - 使用内建泛型 (PEP 585): `list[int]`、`dict[str, float]`
  - 对外 API 绝不留 `Any`
  - 善用 `Protocol`、`TypedDict`、`Self`、`TypeAlias`、`Literal`
  - 使用 `Final` 避免误改
- **反过度设计原则**: 在开始任何分析前，先问自己：
  1. "这是个真问题还是臆想出来的？" - 拒绝过度设计
  2. "有更简单的方法吗？" - 永远寻找最简方案  
  3. "会破坏什么吗？" - 向后兼容是铁律

### Architecture Patterns
- **Agent 开发模式**: 
  - 可选择三种开发路径：
    1. 在现有的 `agentscope.agent.ReActAgent` 基础上进行开发
    2. 继承 `agentscope.agent.ReActAgentBase` 进行开发
    3. 继承 `agentscope.agent.AgentBase` 进行开发
- **必须实现的接口**:
  - `observe(msg)` 函数：观察和接收消息
  - `__call__(msg)` 或 `__call__()`: 返回合法的 `Msg` 对象
  - `reply(msg)`: 返回合法的 `Msg` 对象
  - 结构化输出: 支持 `agent(msg, structured_model=StructuredModel)` (StructuredModel 为 `pydantic.BaseModel` 的子类)
  - 状态管理: 支持 `state_dict()` 和 `load_state_dict()` 函数
- **框架特性**:
  - 透明化设计：所有操作对开发者可见可控
  - 模块化组件：LEGO 风格的 Agent 构建
  - 支持异步执行、实时中断、并行工具调用
  - 自动状态管理和长期记忆

### Testing Strategy
- **游戏测试**: 运行 `examples/game/werewolves/main.py` 进行完整游戏测试
- **Agent 代码位置**: `examples/agent_werewolves/`
- **环境变量**: `DASHSCOPE_API_KEY` 已配置，无需额外设置

### Git Workflow
- **当前分支**: `cursor-optimize/werewolves`
- **代码安全**: 可以放心删除不需要的代码，git 有版本备份
- **提交规范**: 遵循清晰的提交信息描述

## Domain Context

### 狼人杀游戏规则
- **游戏模式**: 九人制狼人杀
- **游戏目标**: 通过推理、发言、投票等策略获胜
- **角色类型**: 包括狼人、平民、预言家、女巫等不同角色
- **关键能力**:
  - 动态环境适应：根据游戏进程调整策略
  - 自主学习：从游戏经验中学习和优化
  - 策略制定：根据角色和局势制定最优策略
  - 信息推理：基于有限信息进行逻辑推理

### Agent 设计考量
- 需要处理不完全信息博弈
- 需要进行多轮对话和投票决策
- 需要识别和应对欺骗策略
- 需要团队协作（好人阵营）或伪装（狼人阵营）

## Important Constraints

### 技术约束
1. **必须使用 AgentScope 1.0 框架** - 这是比赛硬性要求
2. **必须使用百炼平台的 qwen-max 模型** - 指定的大模型服务
3. **Agent 调用方式**:
   - 必须支持: `agent(msg)` (msg 为 `agentscope.message.Msg` 实例)
   - 必须支持: `agent()`
   - 必须支持: `agent(msg, structured_model=StructuredModel)`
4. **必须实现的接口**:
   - `observe()` 函数
   - 结构化输出功能（基于 `BaseModel`）
   - Session 读取和保存（`state_dict()` 和 `load_state_dict()`）
   - `__call__()` 和 `reply()` 返回合法的 `Msg` 对象

### 性能约束
- Agent 需要在合理时间内做出决策
- 需要考虑 API 调用成本和延迟

### 业务约束
- 这是比赛项目，需要在规定时间内完成
- 最终目标是提升游戏胜率

## External Dependencies

### API 服务
- **DashScope API**: 百炼平台的 API 服务
  - 环境变量: `DASHSCOPE_API_KEY` (已配置)
  - 用途: 调用 qwen-max 模型
  - 相关类: `agentscope.model.DashScopeChatModel`

### AgentScope 核心模块
- **Agent**: `agentscope.agent.ReActAgent`, `ReActAgentBase`, `AgentBase`
- **Model**: `agentscope.model.DashScopeChatModel`
- **Formatter**: `agentscope.formatter.DashScopeChatFormatter`
- **Memory**: `agentscope.memory.InMemoryMemory`
- **Message**: `agentscope.message.Msg`
- **Tool**: `agentscope.tool.Toolkit`
- **Session**: 用于状态管理

### 开发工具
- **uv**: Python 环境和包管理工具
  - 创建环境: `uv venv --python 3.12`
  - 新增包: `uv add <package>`
- **ruff**: 代码格式化工具
  - 格式化: `ruff format`
- **pyright**: 类型检查器，规则已固化
