# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

AgentScope 是一个以开发者为中心的框架，用于构建智能体应用。它提供了一个灵活而强大的多智能体平台，支持：

- **面向多智能体**：专为多智能体系统设计，具有明确的消息传递和工作流编排
- **模型无关性**：一次编程，支持所有模型（OpenAI、Anthropic、DashScope、Ollama、Google Gemini 等）
- **乐高式智能体构建**：所有组件都是模块化和独立的
- **实时控制**：原生支持实时中断和自定义处理
- **智能体特性**：支持智能体工具管理、长期记忆控制和智能体 RAG

## 仓库结构

```
agentscope/
├── src/agentscope/           # 主源代码
│   ├── agent/               # 智能体基类和实现
│   ├── model/               # 不同 LLM 提供商的模型封装
│   ├── tool/                # 内置工具和工具包管理
│   ├── pipeline/            # 工作流编排和多智能体对话管理
│   ├── memory/              # 内存管理系统
│   ├── message/             # 消息处理和格式化
│   ├── formatter/           # 不同模型提供商的提示格式化
│   ├── session/             # 会话和状态管理
│   ├── embedding/           # 嵌入模型和工具
│   ├── token/               # 不同提供商的令牌计数
│   ├── evaluate/            # 评估框架
│   ├── tracing/             # 基于 OpenTelemetry 的追踪
│   ├── rag/                 # RAG（检索增强生成）组件
│   ├── mcp/                 # MCP（模型控制协议）集成
│   ├── plan/                # 规划和推理模块
│   └── hooks/               # 扩展功能的钩子系统
├── tests/                   # 单元测试和集成测试
├── examples/                # 示例应用和用例
├── docs/                    # 文档
└── assets/                  # 图像和其他资源
```

## 开发命令

### 安装

```bash
# 开发模式安装
pip install -e .

# 安装所有依赖
pip install -e .[dev]
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/model_openai_test.py

# 运行带覆盖率的测试
pytest --cov=src/agentscope tests/
```

### 代码质量

项目使用 pre-commit 钩子来强制执行代码质量：

```bash
# 安装 pre-commit 钩子
pre-commit install

# 对所有文件运行 pre-commit
pre-commit run --all-files
```

包括：
- Black（代码格式化）
- Flake8（代码检查）
- Pylint（静态分析）
- MyPy（类型检查）
- 各种用于安全性和一致性的 pre-commit 钩子

## 核心架构概念

### 1. 智能体系统
- `AgentBase`：所有智能体的基类
- `ReActAgent`：具有动作规划的推理智能体
- `UserAgent`：处理用户交互
- 智能体通过 `Msg`（消息）对象进行通信

### 2. 模型抽象
- `ChatModelBase`：聊天模型的基类
- 支持多个提供商：OpenAI、Anthropic、DashScope、Ollama、Gemini
- 异步调用支持
- 流式/非流式返回

### 3. 管道系统
- `MsgHub`：管理多智能体对话和消息路由
- `SequentialPipeline`：按顺序执行智能体
- `FanoutPipeline`：并行执行多个智能体
- 复杂智能体交互的工作流编排

### 4. 工具系统
- `Toolkit`：注册和管理工具的容器
- 内置工具用于代码执行、文件操作、多模态处理
- 支持 MCP（模型控制协议）工具

### 5. 内存系统
- 使用 `InMemoryMemory` 的短期内存
- 与 Mem0 集成的长期内存
- 基于会话的状态管理

## 关键开发模式

### 智能体创建
```python
from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.memory import InMemoryMemory

agent = ReActAgent(
    name="assistant",
    sys_prompt="You are a helpful assistant",
    model=OpenAIChatModel(
        model_name="gpt-4",
        api_key=os.environ["OPENAI_API_KEY"]
    ),
    memory=InMemoryMemory()
)
```

### 多智能体对话
```python
from agentscope.pipeline import MsgHub, sequential_pipeline

async with MsgHub(participants=[agent1, agent2, agent3]) as hub:
    await sequential_pipeline([agent1, agent2, agent3])
```

### 工具注册
```python
from agentscope.tool import Toolkit, execute_python_code

toolkit = Toolkit()
toolkit.register_tool_function(execute_python_code)
```

## 文档

- 主文档：https://doc.agentscope.io/
- API 文档：https://doc.agentscope.io/api/agentscope.html
- 示例：`examples/` 目录包含各种用例

## 版本控制

项目遵循语义化版本控制。查看 `src/agentscope/_version.py` 获取当前版本。


# 我现在正常参与一个比赛
### 赛题描述

本赛题需要参赛者基于 AgentScope 1.0 框架构建可以通过自主学习不断提升游戏水平的智能体，该智能体需要适应狼人杀游戏的角色，参与九人制狼人杀比赛，自主制定游戏策略并以游戏获胜为最终目标。该赛题考察Agent在动态环境中的学习能力、适应能力和策略优化能力。

代码所在的目录是 `examples/agent_werewolves`

### 技术要求
**需要选择使用AgentScope 1.0 框架和百炼平台的qwen-max模型。**


- 在现有的agentscope.agent.ReActAgent基础上进行开发
- 继承agentscope.agent.ReActAgentBase进行开发
- 继承agentscope.agent.AgentBase进行开发
- 最终，参赛选手开发的智能体类需要保证满足以下要求，可以通过如下方式调用：

```
agent(msg)  # msg 为`agentscope.message.Msg`类的实例
agent()
agent(msg, structured_model=StructuredModel)  # StructuredModel 为 pydantic.BaseModel 的子类
```

- 必须实现observe函数
- 必须支持基于 BaseModel 的结构化输出功能
- 必须支持 Session 读取和保存，即支持 state_dict() 和 load_state_dict() 函数
- __call__以及reply返回的必须是合法的Msg对象

模型：由于本赛题考察Agent的能力，为避免模型差异带来的影响，参赛选手的智能体只能使用百炼提供的 “qwen-max” 模型。