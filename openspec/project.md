# Project Context

## Purpose
AgentScope 是一个以开发者为中心的框架，用于构建智能体应用。它提供了一个灵活而强大的多智能体平台，支持面向多智能体系统设计，具有明确的消息传递和工作流编排。本项目旨在通过模块化和独立的组件，构建实时控制和自适应的智能体应用，支持智能体工具管理、长期记忆控制和智能体 RAG 等特性。

## Tech Stack
- Python 3.10+
- DashScope API (百炼平台)
- Qwen-Max 模型
- Pydantic for structured output
- AsyncIO for asynchronous operations
- ShortUUID for unique identifiers
- NumPy for numerical computations
- SoundDevice for audio processing
- AgentScope core components (agents, models, memory, tools, pipelines)

## Project Conventions

### Code Style
- 遵循 PEP 8 代码规范
- 使用类型提示 (Type Hints)
- 函数和类需要有完整的文档字符串 (docstrings)
- 变量命名使用下划线分隔 (snake_case)
- 类名使用驼峰命名法 (PascalCase)
- 常量使用大写字母和下划线 (UPPER_CASE)
- 代码格式化使用 Black
- 代码检查使用 Flake8 和 Pylint
- 类型检查使用 MyPy

### Architecture Patterns
- 面向对象设计，使用基类和继承模式
- 模块化设计，各组件独立且可组合
- 异步编程模型，支持并发处理
- 状态管理模式，支持智能体状态的保存和恢复
- 钩子系统，支持扩展功能
- 内存管理，支持短期和长期记忆
- 工具系统，支持动态工具注册和调用

### Testing Strategy
- 单元测试使用 pytest
- 集成测试覆盖核心功能
- 代码覆盖率检查
- 持续集成和持续部署 (CI/CD)
- 使用 pre-commit 钩子确保代码质量

### Git Workflow
- 使用功能分支开发模式
- 主分支为 main，开发分支为 dev
- 提交信息遵循约定式提交规范
- 代码审查通过后合并到主分支
- 版本控制遵循语义化版本控制

## Domain Context
AgentScope 框架专注于多智能体系统的构建和管理，支持各种应用场景，包括但不限于：
- 狼人杀游戏智能体
- 多智能体对话系统
- 任务规划和执行
- 知识检索和增强生成 (RAG)
- 工具调用和 API 集成
- 长期记忆和上下文管理

智能体通过消息 (Msg) 对象进行通信，支持文本、工具调用、工具结果等多种消息类型。框架提供了丰富的组件，包括智能体基类、模型抽象、内存管理、工具系统、管道系统等，开发者可以根据需求灵活组合使用。

## Important Constraints
- 智能体必须使用百炼平台的 qwen-max 模型
- 必须实现 observe 函数
- 必须支持基于 BaseModel 的结构化输出功能
- 必须支持 Session 读取和保存，即支持 state_dict() 和 load_state_dict() 函数
- __call__ 以及 reply 返回的必须是合法的 Msg 对象
- 智能体需要支持自学习和策略优化能力
- 代码需要遵循 AgentScope 框架的设计模式和规范

## External Dependencies
- DashScope SDK for model API access
- Pydantic for structured data validation
- ShortUUID for unique ID generation
- NumPy for numerical operations
- SoundDevice for audio processing (可选)
- Various standard Python libraries (asyncio, json, os, etc.)